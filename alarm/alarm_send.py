# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import requests
import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper, http_helper




class AlarmSend(object):

    def __init__(self, logName):
        # print config
        self.logPath = os.path.join(config.log_floder, logName+'.log')
        
        pass

    def __repr__(self):
        """Return the raw stats."""
        return self.stats

    def __str__(self):
        """Return the human-readable stats."""
        return str(self.stats)


    def get_alarm_logger(self):
        ''' 获取采集数据日志对象 '''
        return log_helper.get_logger(self.logPath)


    _query_alarm_sql = ''' SELECT a.`id`, a.`serverId`, a.`serverIp`, a.`level`, a.`type`, a.`limitValue`, 
                                    a.`nowValue`, a.`msg`, a.`collectTime`, a.`monitorTime`, a.`status`, 
                                    a.`mobiles`, a.`sendTime` , b.`platId` AS `serverPlatId`, b.`appId` AS `serverAppId` 
                            FROM `soc_sm_alarm` AS a 
                            LEFT JOIN `soc_sm_server` AS b ON b.`id` = a.`serverId` '''
    _query_alarm_col = ['id', 'serverId', 'serverIp', 'level', 'type', 'limitValue', 'nowValue', 'msg', 'collectTime', 'monitorTime', 'status', 'mobiles', 'sendTime', 'serverPlatId' ,'serverAppId' ]
    def __query_alarm_by_monitorTime(self, monitorTime):
        ''' 获取需要所有采集的服务器 '''
        sql = AlarmSend._query_alarm_sql + ' WHERE a.`monitorTime` >= %s order by a.`type` desc, a.`id` asc '
        params = (monitorTime, )
        alarms = mysql_helper.get_mysql_helper(**config.db).find_all(sql, params, AlarmSend._query_alarm_col)
        return alarms


    _update_sql = ''' UPDATE `soc_sm_alarm` SET `status` = %s ,`sendTime` = now() WHERE `serverId` = %s AND `type` = %s AND `status` = %s '''
    def __update_alarm_status(self, serverId, typee, status):
        params = (status, serverId, typee, 1, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AlarmSend._update_sql, params)
        pass


    __add_alarm_sql = ''' INSERT INTO soc_sm_alarm(`serverId`, `serverIp`, `level`, `type`, `limitValue`, `nowValue`, `msg`, `collectTime`, `monitorTime`, `status`, `mobiles`) VALUES (%s, %s, %s, %s, %s, %s, %s, now(), now(), %s, %s) '''

    def add_repair_alarm(self, id, ip, level, typee, limitValue = 0, nowValue = 0, msg = '', mobiles = ''):
        sql = AlarmSend.__add_alarm_sql
        params = (id, ip, level, typee, limitValue, nowValue, msg, 6, mobiles)
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(sql, params)
        pass

    def alarm_format(self, alarms):
        ''' 整理报警列表 '''
        alarmMap = {}

        for a in alarms:
            key = '%d_%s' % (a['serverId'], a['type'])

            alarmMap[key] = alarmMap.get(key, {})

            if None == alarmMap[key].get('collectTime', None):
                alarmMap[key]['beginCollectTime'] = a['collectTime']

            alarmMap[key]['collectTime'] = a['collectTime']

            if 1 == a['status'] and 3 != alarmMap[key].get('isSend', 1):
                alarmMap[key]['isSend'] = 1
            else:
                alarmMap[key]['isSend'] = 3

            if 6 == a['status']:
                alarmMap[key]['isSend'] = 6


            alarmMap[key]['status'] = a['status']            
            alarmMap[key]['mobiles'] = a['mobiles']
            alarmMap[key]['serverIp'] = a['serverIp']
            alarmMap[key]['msg'] = a['msg']
            alarmMap[key]['serverId'] = a['serverId']
            alarmMap[key]['type'] = a['type']
            alarmMap[key]['level'] = a['level']
            alarmMap[key]['limitValue'] = a['limitValue']
            alarmMap[key]['nowValue'] = a['nowValue']
            alarmMap[key]['serverPlatId'] = a['serverPlatId']
            alarmMap[key]['serverAppId'] = a['serverAppId']

        return alarmMap


    def send_sms(self, mobiles, msg):
        ms = mobiles.split(',')
        # ms = ['18917637631']

        for m in ms:
            if str_helper.is_null_or_empty(m):
                continue
            params = config.sms_params
            params['phone'] = m
            params['msg'] = msg
         
            r = requests.get(url = config.sms_api, params = params)
            l = 'sms_req_url:%s;status:%d;result:%s' % (r.url, r.status_code, r.text)
            self.get_alarm_logger().info(l)
            time.sleep(1)


    def alarm_send_run(self):
        while True:
            time.sleep(config.analysis_interval)

            monitorTime = date_helper.get_datetimestr(minutes = -config.alarm_repeat_time)
            overTime = date_helper.datetime_to_time(date_helper.get_add_datetime(minutes = -config.alarm_repair_time))
            try:
                alarms = self.__query_alarm_by_monitorTime(monitorTime)
                # print len(alarms)
                alarmMap = self.alarm_format(alarms)
                self.get_alarm_logger().info(str_helper.json_encode(alarmMap))
                for k, v in alarmMap.items():
                    if overTime > date_helper.datetime_to_time(v['collectTime']) and 3 == v['isSend'] :
                        ''' 发送恢复短信 '''
                        msg = '['+v['collectTime'].strftime('%Y%m%d %H%M%S')+']故障已恢复' + v['serverIp'] + '#' + v['serverPlatId'] + '#' + v['serverAppId'] + v['msg']
                        self.send_sms(v['mobiles'], msg)
                        self.add_repair_alarm(id = v['serverId'], ip = v['serverIp'], level = config.alarm_level, typee = v['type'], limitValue = 0, nowValue = 0, msg = msg, mobiles = v['mobiles'])                        
                    elif 1 == v['isSend'] :
                        ''' 发送报警短信 '''
                        self.send_sms(v['mobiles'], '['+v['collectTime'].strftime('%Y%m%d %H%M%S')+']' + v['serverIp'] + '#' + v['serverPlatId'] + '#' + v['serverAppId'] + v['msg'])
                        self.__update_alarm_status(serverId = v['serverId'], typee = v['type'], status = 3)
                    else:
                        ''' 已发送过报警短信，不重复发送 '''
                        a = 1
                    

            except Exception, e:
                self.get_alarm_logger().error(traceback.format_exc())
            finally:
                pass



        
