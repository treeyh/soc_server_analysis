# -*- coding: utf-8 -*-


import sys
import os
import time
import traceback

import psutil

import config
from helper import log_helper, mysql_helper, str_helper, date_helper, file_helper
from alarm.alarm_send import AlarmSend




def main():
    ''' 报警短信主进程 '''
    cls = AlarmSend('alarm_send')
    cls.alarm_send_run()



if __name__ == '__main__':    
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')    
   
    main()

    


