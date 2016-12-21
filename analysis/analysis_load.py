# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisLoad(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisLoad, self).__init__(mqName)

    __update_sql = '''UPDATE soc_sm_server SET `cpuCount` = %s WHERE `id` = %s '''

    def update_info(self, id, ip, dt, info):
        ''' 更新服务器cpu核数 '''
        if None == info or len(info) <= 0:
            return

        cpuCount = info['cpucore']
        
        params = (cpuCount, id, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisLoad.__update_sql, params)
        

    __add_sql = '''INSERT INTO soc_sm_server_load(`serverId`, `min1`, `min5`, `min15`, `collectTime`, `monitorTime` ) VALUES (%s, %s, %s, %s, %s, now())'''
    def add_info(self, id, ip, dt, info):
        ''' 保存服务器负载情况 '''
        if None == info:
            return
        min1 = info['min1']
        min5 = info['min5']
        min15 = info['min15']
        params = (id, min1, min5, min15, dt, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisLoad.__add_sql, params)
        
    
    def analysis(self):
        ''' 分析日志 '''
        self.get_run_logger().info(self.mqName+'_start...')
        
        while True:            
            try:
                obj = self.get_new_log()
                if None == obj:
                    self.get_run_logger().info(self.mqName+'_sleep...')
                    time.sleep(config.analysis_interval)
                    continue

                id = obj['id']
                ip = obj['ip']
                dt = obj['time']
                info = obj['info']
                cpucore = info['cpucore']
                min1 = info['min1']
                min5 = info['min5']
                min15 = info['min15']

                server = self.get_server_by_id(id)
                if None == server.get('cpuCount', None):
                    self.update_info(id, ip, dt, info)

                self.add_info(id, ip, dt, info)                
                if min1 > 30.0:
                    msg = '服务器负载1分钟%s,5分钟%s,15分钟%s' % (str(min1), str(min5), str(min15))
                    mobiles = self.get_server_alarm_mobiles(id)
                    self.add_alarm(id = id, ip = ip, level = config.alarm_level, limitValue = 30.0, nowValue = percent, msg = msg, dt = dt, mobiles = mobiles)
                    continue

            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        