# -*- coding: utf-8 -*-


import sys
import os
import time
import datetime
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisMonitor(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisMonitor, self).__init__(mqName)



    def analysis(self):
        ''' 分析日志 '''
        self.get_run_logger().info(self.mqName+'_start...')
        
        while True:
            self.get_run_logger().info(self.mqName+'_sleep...')
            time.sleep(config.analysis_monitor_interval) 
            checkTime = date_helper.datetime_to_time(date_helper.get_add_datetime(minutes = -config.alerm_server_monitor_time))

            try:
                servers = self.query_collect_server_all()
                if None == servers or len(servers) <= 0:
                    self.get_run_logger().info(self.mqName+'_sleep...')
                    time.sleep(config.analysis_interval)
                    continue

                for server in servers:
                    lastMonitorTime = date_helper.datetime_to_time(server['lastMonitorTime'])
                    if lastMonitorTime < checkTime:
                        msg = '服务器超过%s分钟未采集状态,最后一次采集时间%s.' % (str(config.alerm_server_monitor_time), server['lastMonitorTime'].strftime('%Y%m%d %H%M%S'))
                        mobiles = self.get_server_alarm_mobiles(server['id'])
                        self.add_alarm(id = server['id'], ip = server['ip'], level = config.alarm_level, limitValue = 0, nowValue = 0, msg = msg, dt = datetime.datetime.now(), mobiles = mobiles)

            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        