# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisFs(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisFs, self).__init__(mqName)


    
    
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

                for i in info:
                    mnt_point = i[i['key']]
                    used = i['used']
                    percent = i['percent']
                    free = i['free']
                    size = i['size']

                    if percent > 80.0:
                        msg = '服务器%s空间占用%s%%,使用%sMb,总量%sMb.' % (mnt_point, str(percent), str(used/1024/1024), str(size/1024/1024))
                        mobiles = self.get_server_alarm_mobiles(id)
                        self.add_alarm(id = id, ip = ip, level = config.alarm_level, limitValue = 80.0, nowValue = percent, msg = msg, dt = dt, mobiles = mobiles)
                        continue


            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        