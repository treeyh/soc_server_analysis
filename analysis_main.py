# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase
from analysis.analysis_cpu import AnalysisCpu
from analysis.analysis_diskio import AnalysisDiskio
from analysis.analysis_fs import AnalysisFs
from analysis.analysis_ip import AnalysisIp
from analysis.analysis_load import AnalysisLoad
from analysis.analysis_mem import AnalysisMem
from analysis.analysis_memswap import AnalysisMemswap
from analysis.analysis_network import AnalysisNetwork
from analysis.analysis_now import AnalysisNow
from analysis.analysis_percpu import AnalysisPercpu
from analysis.analysis_processcount import AnalysisProcesscount
from analysis.analysis_processlist import AnalysisProcesslist
from analysis.analysis_quicklook import AnalysisQuicklook
from analysis.analysis_system import AnalysisSystem
from analysis.analysis_uptime import AnalysisUptime
from analysis.analysis_monitor import AnalysisMonitor





def logger():
    logPath = os.path.join(config.log_floder, 'analysis_start_run.log')
    return log_helper.get_logger(logPath)

def main():
    ''' 启动分析进程 '''

    _collect_py_path = os.path.join(config.shell_root_path, config.analysis_py)

    for t in config.collect_types:
        cmd = '%s %s %s' % (config.analysis_start_python_path, _collect_py_path, t)
        logPath = os.path.join(config.log_floder, t+'shell', t+'.log')
        file_helper.mkdirs(logPath, False)
        shell = '''#!/bin/bash 
nohup %(cmd)s >> %(logPath)s &
sleep 3s
echo $!''' % {'cmd':cmd, 'logPath' : logPath}
  
        re = os.popen(shell)
        
        pid = re.read().strip()
        logger().info('shellcmd:' + shell + ';result:' + pid)
        
        try:
            pidpath = os.path.join(config.shell_root_path, 'pid', t + '.pid')
            file_helper.write_file(pidpath, pid, 'w')
        except Exception, e:
            logger().error(traceback.format_exc())
    pass


def run(model):
    ''' 启动对应分析模块 '''
    logger().info(model + ' start')

    try:
        # logger().info(globals())
        cls = globals()['Analysis'+model.capitalize()](model)
        cls.analysis()
    except Exception, e:
        logger().info(model+' start_error:'+traceback.format_exc())
    finally:
        pass
    



if __name__ == '__main__':    
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')    

    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        main()

    



# if __name__ == '__main__':
#     a = AnalysisBase('a')
#     import datetime
#     print a.add_alarm(1, '192.168.23.71', 5, 5, 6, '123123', datetime.datetime.now(), '18917637631,15721282565')    