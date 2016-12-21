# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisDiskio(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisDiskio, self).__init__(mqName)


    __add_sql = '''INSERT INTO soc_sm_server_diskio( `serverId`, `diskName`, `readBytes`, `writeBytes`, `collectTime`, `monitorTime` ) VALUES ( %s, %s, %s, %s, %s, now())'''
    
    def add_info(self, id, ip, dt, info):
        ''' 保存服务器负载情况 '''
        if None == info or len(info) <= 0:
            return

        for i in info:
            diskName = i[i['key']]
            readBytes = i['read_bytes']
            writeBytes = i['write_bytes']
            params = (id, diskName, readBytes, writeBytes, dt, )
            mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisDiskio.__add_sql, params)

    
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

                self.add_info(id, ip, dt, info)
                
            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        