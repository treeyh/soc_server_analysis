# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisCpu(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisCpu, self).__init__(mqName)


    
    __add_sql = '''INSERT INTO soc_sm_server_cpu(`serverId`, `softirq`, `iowait`, `system`, `guest`, `idle`, `user`, `irq`, `total`, `steal`, `nice`, `collectTime`, `monitorTime` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()) '''
    def add_info(self, id, ip, dt, info):        
        if None == info:
            return
        params = (id, info['softirq'], info['iowait'], info['system'], info['guest'], info['idle'], info['user'], info['irq'], info['total'], info['steal'], info['nice'], dt, )
        mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisCpu.__add_sql, params)

    
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

                total = info['total']

                self.add_info(id, ip, dt, info)

                if total > 80.0:
                    msg = '服务器CPU负载%s%%' % (str(total))
                    mobiles = self.get_server_alarm_mobiles(id)
                    self.add_alarm(id = id, ip = ip, level = config.alarm_level, limitValue = 80.0, nowValue = percent, msg = msg, dt = dt, mobiles = mobiles)
                    continue

            except Exception, e:
                self.get_run_logger().error(traceback.format_exc())
                time.sleep(config.analysis_interval)
            finally:
                pass
    



        