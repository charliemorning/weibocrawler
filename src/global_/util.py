# -*- coding: UTF-8 -*-
"""
#=============================================================================
#     FileName: util.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:53
#      History:
#=============================================================================
"""
import urllib
import urllib2
import cookielib
import exceptions


def makeGetPara(para):
    raw = ""
    
    for key in para:
        val = para[key]
        raw += key + "=" + val + "&"
    
    if len(raw) > 0:
        return raw[:-1]
    else:
        return raw


def get(url, para=None, cookie=None, **kwargs):
    """
    To act a GET request to specific URL.
    @para url: the specific 
    @para para:
    @para cookie: 
    @return: the response of server
    """

    paraStr = ""
    if para is not None:
        if type(para) is type({}):
            if len(para) != 0:
                paraStr += "?" + makeGetPara(para)


    urlWithPara = url + paraStr


    success = False
    times = 0
    while not success or times > 5:

        try:
            if cookie is None:
                ret = urllib2.urlopen(urlWithPara, timeout=10)
            else:
                if 'receive' in kwargs and kwargs['receive'] is True:
                    pass
                else:
                    cookie.load()
                cookieJar = urllib2.HTTPCookieProcessor(cookie)
                opener = urllib2.build_opener(cookieJar)
                print urlWithPara
                req = urllib2.Request(urlWithPara, 
                    headers={
                    'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0",
                    'Connection' : 'keep-alive',
                    'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'
                    }) 
                ret = opener.open(req)
                cookie.save()

        except urllib2.URLError as e:
            print 'URLError: %s'%urlWithPara
            times += 1
        except urllib2.HTTPError as e:
            print e.code
            times += 1
        else:
            return ret

    if success is False:
        raise exceptions.Exception()

def post(url, data, cookie=None, **kwargs):
    
    #构造POST请求参数
    data = urllib.urlencode(data)
   
    success = False
    times = 0

    while not success or times > 5:

        try:
    
            if cookie is None:
                ret = urllib2.urlopen(url, data, timeout=10)
            else:
                if 'receive' in kwargs and kwargs['receive'] is True:
                    pass
                else:
                    cookie.load()

                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

                opener.addheaders.append(('User-Agent' , 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0'))
                   
                opener.addheaders.append(('Connection' , 'keep-alive'))
                opener.addheaders.append(('Accept-Language' , 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'))

            
                #进行连接
                ret = opener.open(url, data)
                #保存cookie
                cookie.save() 
        except urllib2.URLError as e:
            print 'URLError: %s'%url
            times += 1
        except urllib2.HTTPError as e:
            print e.code
            times += 1
        else:
            return ret

    if success is False:
        raise exceptions.Exception()

    


