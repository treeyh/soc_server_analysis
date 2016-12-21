# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisMem(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisMem, self).__init__(mqName)



    __update_sql = '''UPDATE soc_sm_server SET `memory` = %s WHERE `id` = %s '''

    def update_info(self, id, ip, dt, info):
        ''' 更新服务器总内存 '''
        if None == info or len(info) <= 0:
            return

        total = info['total']
        
        params = (total, id, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisMem.__update_sql, params)


    __add_sql = '''INSERT INTO soc_sm_server_mem(`serverId`, `available`, `used`, `cached`, `percent`, `free`, `inactive`, `active`, `total`, `buffers`, `collectTime`, `monitorTime` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()) '''
    
    def add_info(self, id, ip, dt, info):
        ''' 保存服务器内存情况 '''
        if None == info:
            return        
        params = (id, info['available'], info['used'], info['cached'], info['percent'], info['free'], info['inactive'], info['active'], info['total'], info['buffers'], dt, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisMem.__add_sql, params)
        




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

                server = self.get_server_by_id(id)
                if None == server.get('memory', None):
                    self.update_info(id, ip, dt, info)

                self.add_info(id, ip, dt, info)
                percent = info['percent']
                if percent > 80.0:
                    msg = '服务器内存占用%s%%' % (str(percent))
                    mobiles = self.get_server_alarm_mobiles(id)
                    self.add_alarm(id = id, ip = ip, level = config.alarm_level, limitValue = 80.0, nowValue = percent, msg = msg, dt = dt, mobiles = mobiles)

            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        