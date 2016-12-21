# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



class AnalysisNetwork(AnalysisBase):

    def __init__(self, mqName):
        super(AnalysisNetwork, self).__init__(mqName)


    __query_sql = ''' SELECT a.`id`, a.`serverId`, a.`netCard`, a.`tx`, a.`totalTx`, a.`rx`, a.`totalRx`, a.`cx`, a.`totalcx`, a.`collectTime`, a.`monitorTime` FROM `soc_sm_server_network` AS a '''
    __query_col = ['id', 'serverId', 'netCard', 'tx', 'totalTx', 'rx', 'totalRx', 'cx', 'totalcx', 'collectTime', 'monitorTime' ]

    __add_sql = ''' INSERT INTO soc_sm_server_network( `serverId`, `netCard`, `tx`, `totalTx`, `rx`, `totalRx`, `cx`, `totalcx`, `collectTime`, `monitorTime` ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, now())  '''


    def add_info(self, id, ip, dt, info):
        if None == info or len(info) <= 0:
            return

        for i in info:
            params = (id, i[i['key']], i['tx'], i['cumulative_tx'], i['rx'], i['cumulative_rx'], i['cx'], i['cumulative_cx'], dt, )
            mysql_helper.get_mysql_helper(**config.db).insert_or_update_or_delete(AnalysisNetwork.__add_sql, params)


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
    



        