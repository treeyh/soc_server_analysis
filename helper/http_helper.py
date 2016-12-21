#-*- encoding: utf-8 -*-

import urllib
import urllib2
import socket
import sys
import cookielib

from os.path import basename
from urlparse import urlsplit

_req_type = False
try:
    import requests
    _req_type = True
except Exception, e:
    pass
    


cookies = None

###GB18030
def http(url, params = {}, headers = {}, method = 'GET', timeout=socket._GLOBAL_DEFAULT_TIMEOUT, isCookie = False, htmlEncode = 'UTF-8', exportEncode = 'UTF-8', resp=['content']):
    '''  
        HTTP 模拟请求
        url：请求地址
        params：传入参数，map形式传入
        headers：模拟http头
        method：http请求模式，默认GET
        timeout：超时时间
        htmlEncode：请求内容的编码，默认UTF-8
        exportEncode：输出内容编码，默认UTF-8
        resp：返回输出内容，默认content（http内容），还支持code,info,url
    '''
    try:
        if True == isCookie:
            global cookies
            if None == cookies:                
                cookies = cookielib.CookieJar()
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
                urllib2.install_opener(opener)

        req = None
        if 'GET' == method:
            data = urllib.urlencode(params)
            url = '%s?%s' % (url , data)
            req = urllib2.Request(url = url, headers = headers)
        else:

            if isinstance(params, dict):
                data = urllib.urlencode(params)
            else:
                data = params
            req = urllib2.Request(url = url, data = data, headers = headers)
        
        page = urllib2.urlopen(req, timeout=timeout)
        respinfo = {}
        if 'content' in resp:
            content = page.read()
            if htmlEncode != exportEncode:
                content = content.decode(htmlEncode).encode(exportEncode)
            if len(resp) == 1:
                return content
            respinfo['content'] = content
        if 'code' in resp:
            respinfo['code'] = page.getcode()
        if 'url' in resp:
            respinfo['url'] = page.geturl()
        if 'info' in resp:
            respinfo['info'] = page.info();
        return respinfo
    except:
        print "Unexpected error:", sys.exc_info()
        return None


def url2name(url):
    return basename(urlsplit(url)[2])

def http_download(url, path = None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url:
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    if path:
        # we can force to save the file as specified name
        localName = path
    f = open(localName, 'wb')
    f.write(r.read())
    f.close()
    return None


#http://www.python-requests.org/en/latest/
def get(url, params = None, headers = None, cookies = None, timeout = 20, allow_redirects = True):
    '''
        使用requests扩展调用http-get
        url:访问url
        params:get参数
        headers:http头
        cookie:传入cookie
        timeout:超时时间，秒
        allow_redirects:是否支持跳转，默认为True支持
    '''
    r = requests.get(url = url, params = params, headers=headers, cookies=cookies)
    # print r.url
    return r

def post(url, params = None, data = None, headers = None, filePath = None, cookies = None, allow_redirects = True):
    files = None
    if filePath != None:
        files = {'file': open(filePath, 'rb')}
    r = requests.post(url = url, params = params, data = data, files = files, headers=headers, cookies=cookies)
    return r


if __name__ == '__main__':
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)

    # url = 'http://219.151.3.20:8003/api/SendClientMsg'
    # # host = 'www.163.com'
    # params = {
    # 'body': '{"touser":"oQYbkjniDEjvcl0Z7l6_uQPA8Hb8","msgtype":"news","news":{"articles":[{"title":"云岩区","description":"购物休闲娱乐餐饮一条龙服务，适合和家人，伴侣一起享受的shopping时光","url":"http://219.151.11.197/wxyy/hd/jmsh/yun-a.html","picurl":"http://219.151.11.197/wxyy/hd/jmsh/img/200.jpg"},{"title":"南明区","description":"停下匆匆的脚步，在悠扬悦耳的音乐声中吃吃喝喝，享一段属于自己的休闲时光","url":"http://219.151.11.197/wxyy/hd/jmsh/nan.html","picurl":"http://219.151.11.197/wxyy/hd/jmsh/img/02.jpg"},{"title":"观山湖区","description":"生态型、园林式的现代化新城","url":"http://219.151.11.197/wxyy/hd/jmsh/guan.html","picurl":"http://219.151.11.197/wxyy/hd/jmsh/img/03.jpg"},{"title":"贵州师大商圈","description":"致我们逝去的青春生活之最佳选择，一切尽在不言中","url":"http://219.151.11.197/wxyy/hd/jmsh/daxue.html","picurl":"http://219.151.11.197/wxyy/hd/jmsh/img/04.jpg"},{"title":"都匀市","description":"碧玉般的剑江水，沿江两岸莺语流花，青山耸翠","url":"http://219.151.11.197/wxyy/hd/jmsh/du.html","picurl":"http://219.151.11.197/wxyy/hd/jmsh/img/05.jpg"}]}'
    # }
    # # params = '''{"ToUserName":"gh_485b819861e6","FromUserName":"o6LRKt_KbJ_-Xig8ynE7M9xY-HSg","CreateTime":"1409550598","MsgType":"event","Event":"subscribe"}'''
    # c = http(url = url, params = params, method = 'POST')
    # print c
    
    params = {'a':1}
    url = 'http://127.0.0.1:10004/wxadmin/view/test.php'
    data = {'b':2}
    files = {'file': open('d:\\1.txt', 'rb')}
    r = requests.post(url = url, params = params, data = data, files = files)
    print r.url
    print r.encoding
    print r.text
    print r.status_code
    print r.headers
    print r.history

    url = 'https://github.com'
    r = requests.get(url = url)
    print r.encoding
    print r.text

    # r.status_code == requests.codes.ok


    
    # print len(cookies)

    # print http('http://www.dianping.com/shop/9956592')

