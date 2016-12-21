# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from analysis.analysis_base import AnalysisBase



def logger():
    return log_helper.get_logger(config.log_run_path)


_query_sql = ''' SELECT  a.`id`, a.`name`, a.`osName`, a.`osVersion`, a.`hostname`, a.`ip`, a.`platId`, a.`appId`, a.`cpuCount`, a.`uptime`, a.`lastMonitorTime`, a.`remark`, a.`status`, a.`isDelete`, a.`creater`, a.`createTime`, a.`lastUpdater`, a.`lastUpdateTime` FROM `soc_sm_server` AS a  '''
_query_col = ['id', 'name', 'osName', 'osVersion', 'hostname', 'ip', 'platId', 'appId', 'cpuCount', 'uptime', 'lastMonitorTime', 'remark', 'status', 'isDelete', 'creater', 'createTime', 'lastUpdater', 'lastUpdateTime' ]
def query_collect_server_all():
    ''' 获取需要所有采集的服务器 '''
    global _query_sql
    global _query_col
    sql = _query_sql + ' WHERE a.`status` = %s AND a.`isDelete` = %s order by a.`id` asc '
    params = ( 1, 2, )
    servers = mysql_helper.get_mysql_helper(**config.db).find_all(sql, params, _query_col)
    return servers


def get_run_collect_process():
    ''' 获取当前正在执行的采集进程 '''
    global _collect_py_path
    cmd = config.collect_process_cmd
    pss = os.popen(cmd).readlines()
    
    tasks = {}
    for l in pss:
        ll = l.strip().split(_collect_py_path)
        if len(ll) != 2:
            continue

        lls = ll[1].strip().split(' ')
        if len(lls) != 2:
            continue

        task = {
            'id' : int(lls[0]),
            'ip' : lls[1],
        }

        tasks[task['id']] = task
    return tasks


def start_collects(tasks, collects):
    ''' 启动未执行的采集任务 '''
    global _collect_py_path
    for k, v in tasks.items():
        if None != collects.get(k, None):
            continue

        cmd = '%s %s %d %s' % (config.collect_start_python_path, _collect_py_path, v['id'], v['ip'])
        logPath = os.path.join(config.log_collect_floder, str(v['id'])+'_'+v['ip']+'.log')
        shell = '''#!/bin/bash 
nohup %(cmd)s >> %(logPath)s &
sleep 3s
echo $!''' % {'cmd':cmd, 'logPath':logPath}
  
        re = os.popen(shell)
        
        pid = re.read().strip()
        logger().info('shellcmd:' + shell + ';result:' + pid)
        
        try:
            pidpath = os.path.join(config.shell_root_path, 'pid', str(v['id'])+'_'+v['ip'] + '.pid')
            file_helper.write_file(pidpath, pid, 'w')
        except Exception, e:
            logger().error(traceback.format_exc())

    pass


def kill_collect(id, ip):
    ''' kill采集进程 '''
    pidpath = os.path.join(config.shell_root_path, 'pid', str(id)+'_'+ ip + '.pid')
    pid = file_helper.read_all_file(pidpath, 'r').strip()

    try:
        pid = int(pid)
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            msg = 'kill_process:%s;pid:%d;' % (p.name, pid)
            logger().info(msg)
            p.kill()
    except Exception, e:
        logger().error(traceback.format_exc())
    finally:
        pass




def kill_collects(tasks, collects):
    ''' 删除多余采集任务 '''

    for k, v in collects.items():
        if None != tasks.get(k, None):
            continue

    pass



def collect_run():
    ''' 采集main执行 '''
    servers = query_collect_server_all()
    tasks = {}
    for s in servers:
        tasks[s['id']] = s

    collects = get_run_collect_process()

    logger().info('all_tasks:' + str_helper.json_encode(tasks))
    logger().info('now_tasks:' + str_helper.json_encode(collects))

    start_collects(tasks, collects)
    kill_collects(tasks, collects)



_collect_py_path = ''


def main():
    global _collect_py_path   

    logger().info('collect_main start....')

    _collect_py_path = os.path.join(config.shell_root_path, config.collect_py)

    while True:
        try:
            collect_run()
        except Exception, e:
            logger().error(traceback.format_exc())

        logger().info('collect_main sleep....')
        time.sleep(config.main_interval)



def deco(arg):
  def _deco(func):
    def __deco(a, b):
      print "before %s called [%s]." % (func.__name__, arg)
      print type(func)
      func(a, b)
      print "after %s called [%s]." % (func.__name__, arg)
    return __deco
  return _deco




def _log_result_decorator(fct):
    ''' 记录日志，装饰模式 '''
    def wrapper(*args, **kw):
        ret = fct(*args, **kw)
        print args[0].__class__.__name__
        print args[0].__class__.__module__        
        print fct.__name__
        print fct.func_name
        print ret
        print args
        print kw
        return ret
    return wrapper




@deco("mymodule")
@_log_result_decorator
def myfunc(a = '', b = ''):
  print "myfunc() called."+a+'_'+b
  return 'myfunc(3333)'


class a(object):
    def __init__(self, mqName):
        self.mqName = mqName

    def get_name(self):
        return self.mqName

class b(a):
    def __init__(self, mqName):
        super(b, self).__init__(mqName)




if __name__ == '__main__':
    # myfunc(b = '11', a = 'ab')

#     r= '''UCMQ_HTTP_OK
# {"info": {"cpucore": 24, "min1": 1.45, "min5": 1.22, "min15": 1.1}, "ip": "192.168.23.71", "id": "1", "time": "2015-07-24 16:58:41"}'''
#     print len(r) > 15
#     print r[13:]
#     print str_helper.json_decode(r[13:])

    # print globals()['str_helper']

    # aa = a('a')
    # bb = b('b')
    # print aa.mqName
    # print bb.mqName
    # print aa.get_name()
    # print bb.get_name()

    # a = '2015-07-30 12:12:12'
    # b = '2015-07-30 12:12:50'

    # a = date_helper.str_to_time(a)
    # b = date_helper.str_to_time2(b)
    # print abs(a-b)

    # ab = AnalysisBase('base')
    # print str_helper.json_encode(ab.get_server_by_id(1))
    # print ab.get_server_alarm_mobiles(1)

    # msg = '服务器CPU负载%s%%' % (str(88.0))
    # mobiles = ab.get_server_alarm_mobiles(1)
    # self.add_alarm(id = 1, ip = '1212', level = config.alarm_level, limitValue = 80.0, nowValue = 85.0, msg = msg, dt = datetime.datetime.now(), mobiles = mobiles)

    info = {'a':'a','b':'b'}
    print info
    print len(info)