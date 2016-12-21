# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper, http_helper




class AnalysisBase(object):

    def __init__(self, mqName):
        self.mqName = mqName
        self.logPath = os.path.join(config.log_analysis_floder, mqName, mqName+'.log')
        file_helper.mkdirs(self.logPath, False)

        self.runLogPath = os.path.join(config.log_analysis_floder, mqName+'run', mqName+'.log')        
        file_helper.mkdirs(self.runLogPath, False)

        self.servers = {}
        self.stats = ''
        pass

    def __repr__(self):
        """Return the raw stats."""
        return self.stats

    def __str__(self):
        """Return the human-readable stats."""
        return str(self.stats)


    _query_server_sql = ''' SELECT  a.`id`, a.`name`, a.`osName`, a.`osVersion`, a.`hostname`, a.`ip`, 
                                    a.`platId`, a.`appId`, a.`cpuCount`, a.`memory`, a.`uptime`, a.`alarmId`, b.`userIds`,
                                    a.`lastMonitorTime`, a.`remark`, a.`status`, a.`isDelete`, 
                                    a.`creater`, a.`createTime`, a.`lastUpdater`, a.`lastUpdateTime` 
                            FROM `soc_sm_server` AS a 
                            LEFT JOIN `soc_sm_alarm_group` AS b ON a.`alarmId` = b.`id` '''
    _query_server_col = ['id', 'name', 'osName', 'osVersion', 'hostname', 'ip', 'platId', 'appId', 'cpuCount', 'memory', 'uptime', 'alarmId', 'userIds', 'lastMonitorTime', 'remark', 'status', 'isDelete', 'creater', 'createTime', 'lastUpdater', 'lastUpdateTime' ]
    def query_collect_server_all(self):
        ''' 获取需要所有采集的服务器 '''
        sql = AnalysisBase._query_server_sql + ' WHERE a.`status` = %s AND a.`isDelete` = %s order by a.`id` asc '
        params = ( 1, 2, )
        servers = mysql_helper.get_mysql_helper(**config.db).find_all(sql, params, AnalysisBase._query_server_col)
        return servers

    def __query_collect_server_by_id(self, id):
        ''' 根据ID获取采集的服务器 '''
        sql = AnalysisBase._query_server_sql + ' WHERE a.`id` = %s AND a.`status` = %s AND a.`isDelete` = %s order by a.`id` asc '
        params = ( id, 1, 2, )
        server = mysql_helper.get_mysql_helper(**config.db).find_one(sql, params, AnalysisBase._query_server_col)
        return server


    __query_users_sql = '''SELECT a.`id`, a.`name`, a.`realName`, a.`mobile`, a.`email`, a.`role`, a.`team`, a.`remark`, a.`status`, a.`isDelete`, a.`creater`, a.`createTime`, a.`lastUpdater`, a.`lastUpdateTime` FROM `soc_sm_user` AS a '''
    __query_users_col = ['id', 'name', 'realName', 'mobile', 'email', 'role', 'team', 'remark', 'status', 'isDelete', 'creater', 'createTime', 'lastUpdater', 'lastUpdateTime' ]
    def __get_server_alarm_user(self, userIds):
        ''' 根据服务器报警编号查询报警用户 '''
        users = []
        if None == userIds or '' == userIds:
            return users

        uids = userIds.split(',')
        us = []
        for ui in uids:
            if '' == ui:
                continue
            us.append(ui)

        sql = AnalysisBase.__query_users_sql + ' WHERE a.`status` = %s AND a.`isDelete` = %s AND a.`id` in ('+','.join(us)+') order by a.`id` asc '
        params = ( 1, 2, )
        users = mysql_helper.get_mysql_helper(**config.db).find_all(sql, params, AnalysisBase.__query_users_col)
        return users
        

    def get_server_by_id(self, id):
        ''' 根据ID获取采集的服务器 '''
        if None == self.servers.get(id, None):
            server = self.__query_collect_server_by_id(id)
            users = []
            mobiles = {}
            emails = {}
            if None != server or None != server.get('userIds', None):
                users = self.__get_server_alarm_user(server['userIds'])
                if None != users and len(users) > 0:
                    for user in users:
                        mobiles[user['name']] = user['mobile']
                        emails[user['name']] = user['email']
            server['users'] = users
            server['mobiles'] = mobiles
            server['emails'] = emails
            self.servers[id] = server

        return self.servers[id]


    def get_server_alarm_mobiles(self, id):
        server = self.get_server_by_id(id)
        if None == server or len(server.get('mobiles', {}).values()) <= 0:
            return config.alarm_mobiles
        return ','.join(server.get('mobiles', {}).values())


    __add_alarm_sql = ''' INSERT INTO soc_sm_alarm(`serverId`, `serverIp`, `level`, `type`, `limitValue`, `nowValue`, `msg`, `collectTime`, `monitorTime`, `status`, `mobiles`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), %s, %s) '''

    def add_alarm(self, id, ip, level, limitValue = 0, nowValue = 0, msg = '', dt = '', mobiles = ''):
        sql = AnalysisBase.__add_alarm_sql
        params = (id, ip, level, self.mqName, limitValue, nowValue, msg, dt, 1, mobiles)
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(sql, params)
        pass

    def get_collect_logger(self):
        ''' 获取采集数据日志对象 '''
        return log_helper.get_only_logger(self.logPath)

    def get_run_logger(self):
        ''' 获取运行日志对象 '''
        return log_helper.get_logger(self.runLogPath)


    def get_new_log(self):
        url = config.ucmq_path
        params = {
            'name' : self.mqName,
            'opt' : 'get',
            'ver' : 2,
        }

        re = http_helper.get(url, params = params)
        if 200 == re.status_code:
            re.encoding = 'utf-8'
            log = 'log_info:%s;result:%s' % (re.url, re.text)
            self.get_run_logger().info(log)
            if 'QUE_EMPTY' in re.text:
                return None
            json = re.text[13:].strip()
            self.get_collect_logger().info(json)
            return str_helper.json_decode(json)

        log = 'log_info:%s;resultcode:%d' % (re.url, re.status_code)
        self.get_run_logger().info(log)
        return None


    def _log_result_decorator(fct):
        ''' 记录日志，装饰模式 '''
        def wrapper(*args, **kw):
            ret = fct(*args, **kw)
            # print args[0].__class__.__name__
            # print args[0].__class__.__module__        
            # print fct.__name__
            # print fct.func_name
            # print ret
            # print args
            # print kw
            return ret
        return wrapper

    _log_result_decorator = staticmethod(_log_result_decorator)

