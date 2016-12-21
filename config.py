# -*- coding: utf-8 -*-

#pip install glances
#pip install Bottle 
#pip install netifaces 

import os

#glances 服务端口
glances_port = 61208

#数据库配置
db = {
    'host' : '192.168.36.55', 
    'user' : 'root', 
    'passwd' : 'fXL2bO$RQgaRS^lH', 
    'db' : 'soc_server_monitor',
    'charset' : 'utf8', 
    'port' : 3306,
}

#分析脚本间隔时间，s
analysis_interval = 3

#分析脚本monitor间隔时间，s
analysis_monitor_interval = 60

#日志目录
log_floder = '/data/log/soc_server_analysis'
log_run_path = os.path.join(log_floder, 'run_analysis.log')
log_analysis_floder = os.path.join(log_floder, 'analysis')

#脚本物理绝对路径
shell_root_path = os.path.split(os.path.realpath(__file__))[0]

#采集进程筛选
analysis_process_cmd = 'ps aux|grep [p]ython-soc-server-analysis'
#采集脚本名
analysis_py = 'analysis_main.py'
#分析脚本启动python路径
analysis_start_python_path = '/opt/python/bin/python-soc-server-analysis'


#采集数据节点
collect_types = ['load','ip','memswap','processlist','uptime','percpu','system','diskio','fs','mem','now','quicklook','network','processcount','cpu', 'monitor']

#ucmq path
ucmq_path = 'http://192.168.36.55:8803/'

#服务器监控x分钟未监控进行报警，
alerm_server_monitor_time = 5

#默认报警手机号
alarm_mobiles = '18917637631,15721282565'
#报警级别
alarm_level = 5
#报警避免重复时间，分钟
alarm_repeat_time = 240
#报警恢复短信时间间隔，分钟
alarm_repair_time = 5
#短信报警api
sms_api = 'http://172.16.45.128:80/sendsms'
#短信报警参数
sms_params = {
    'svcid' : '11011',
    'svcpass' : '111111',
    'msgtype' : '9',
    'smstype' : '1',
    'priority' : '3',
}


