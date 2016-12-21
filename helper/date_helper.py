#-*- encoding: utf-8 -*-


from datetime import date, datetime, timedelta
import time





def str_to_time(strtime):
    t_tuple = time.strptime(strtime,"%Y-%m-%d %H:%M:%S")
    return time.mktime(t_tuple)
 
def str_to_time2(strtime):
    dt = datetime.strptime(strtime,"%Y-%m-%d %H:%M:%S")
    t_tuple = dt.timetuple()
    return time.mktime(t_tuple)

def datetime_now_diff(datetimestr):
    '''
        给入的时间字符串，如当前时刻的差值（秒）
    '''
    t_tuple = time.strptime(datetimestr,"%Y-%m-%d %H:%M:%S")
    diff = time.mktime(t_tuple) - time.time()
    return diff


def get_now_datestr():
    return get_add_datetime(days = 0).strftime('%Y-%m-%d')

def get_now_datestr2():
    return get_add_datetime(days = 0).strftime('%Y%m%d')

def get_now_datetimestr():
    return get_add_datetime(days = 0).strftime('%Y-%m-%d %H:%M:%S')

def get_datetimestr_by_time(t):
    return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

def get_now_datetimestr2():
    return datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def get_now_datetimestr3():
    return datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')

def get_add_datest(days):
    return get_add_datetime(days = days).strftime('%Y-%m-%d')

def get_add_datest2(days):
    return get_add_datetime(days = days).strftime('%Y%m%d')

def get_add_datehstr(days):
    return get_add_datetime(days = days).strftime('%Y%m%d%H')

def get_add_datetimestr(days):
    return get_add_datetime(days = days).strftime('%Y-%m-%d %H:%M:%S')

def get_datetimestr(days = 0, seconds = 0, microseconds = 0, milliseconds = 0, minutes = 0, hours = 0, weeks = 0):
    return get_add_datetime(days = days, seconds = seconds, microseconds = microseconds,
                             milliseconds = milliseconds, minutes = minutes, hours = hours, weeks = weeks).strftime('%Y-%m-%d %H:%M:%S')

def get_add_datetime(days = 0, seconds = 0, microseconds = 0, milliseconds = 0, minutes = 0, hours = 0, weeks = 0):
    return datetime.now() + timedelta(days = days, seconds = seconds, microseconds = microseconds,
                                 milliseconds = milliseconds, minutes = minutes, hours = hours, weeks = weeks)


def date_string_to_datetime(string):
    return datetime.strptime(string, "%Y-%m-%d")

def datetime_to_str(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def datetime_to_time(dt):
    return time.mktime(dt.timetuple())


def str_is_date(string):
    '''判断是否是一个有效的日期字符串'''
    try:
        time.strptime(string, '%Y%m%d')
        return True
    except:
        return False

def sleep(second):
    time.sleep(second)


if __name__ == '__main__':
    print get_now_datetimestr3()