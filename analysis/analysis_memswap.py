# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisMemswap(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisMemswap, self).__init__(mqName)

    
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
                used = info['used']
                free = info['free']
                total = info['total']
                percent = info['percent']

                if percent > 30.0:
                    msg = '服务器swap占用%s%%' % (str(percent))
                    mobiles = self.get_server_alarm_mobiles(id)
                    self.add_alarm(id = id, ip = ip, level = config.alarm_level, limitValue = 30.0, nowValue = percent, msg = msg, dt = dt, mobiles = mobiles)
                    continue


            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        