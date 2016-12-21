# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisSystem(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisSystem, self).__init__(mqName)


    __update_sql = '''UPDATE soc_sm_server SET `osName` = %s ,`osVersion` = %s ,`hostname` = %s ,`lastMonitorTime` = now() WHERE `id` = %s '''


    def update_info(self, id, ip, dt, info):
        if None == info or len(info) <= 0:
            return

        osName = info['os_name']
        osVersion = info['os_version']
        linux_distro = info['linux_distro']
        hostname = info['hostname']
        platform = info['platform']
        hr_name = info['hr_name']
        
        params = (linux_distro, osVersion, hostname, id, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisSystem.__update_sql, params)
        


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

                self.update_info(id, ip, dt, info)

            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        