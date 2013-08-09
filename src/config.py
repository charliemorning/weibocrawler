# -*- coding: UTF-8 -*-

import datetime
import codecs
import json

from wglobal import Usages


def init_usage(usg_type):

    if usg_type == u"FetchWeibo":
        usage = Usages.FetchWeibo
    elif usg_type == u"UpdateInfo":
        usage = Usages.UpdateInfo
    elif usg_type == u"FetchFollows":
        usage = Usages.FetchFollows
    elif usg_type == u"Network":
        usage = Usages.Network
    else:
        assert False, u"Wrong Usage Config."

    return usage



def load_config(path):

    f = codecs.open(path, "rb", "UTF-8")
    cfg = json.load(f)
    f.close()

    return cfg

# to load config file
Config = load_config("config.json")

# task of current node
Usage = init_usage(Config["type"])

# depth when crawling the network
Depth = Config["user"]["depth"]

WeiboLimitDate = datetime.datetime(2013, 05, 01, 00, 00, 00)

# unique sequence number in a same type
SEQ = Config["seq"]

# database connection config
Database = {
    "name" : Config["db"]["name"],
    "host" : Config["db"]["host"],
    "port" : Config["db"]["port"]
}

class Cookies:

    # 一般请求时使用的cookie
    RequestCookie = None

    # 登录使用的cookie
    LoginCookie = None 

    # location of cookie which is for login
    LoginCookieFile = '../cookie/login'

    # location of cookie which is for request after login
    CookieFile = '../cookie/cookie'
    
# login page's URL
MobileLoginPageURL = "http://3g.sina.com.cn/prog/wapsite/sso/login.php?backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4&revalid=2&ns=1"

# form action of login
MobileLoginSubmitURL ="http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php?rand=1667505607&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4&revalid=2&ns=1"


BaseURL = "http://weibo.cn/"






# login accounts
account = {}

account["default"] = [{
    'name':"weiboc0001@163.com",
    'password': "1a2b3c"
    # 'gsid':"4uPzb7501qxcj9eq5xNLvc3N53s"
    }]


account[Usages.FetchFollows] = [{
    'name':"weiboc0001@163.com",
    'password': "1a2b3c"
    # 'gsid':"4uPzb7501qxcj9eq5xNLvc3N53s"
    }]

account[Usages.Center] = [{
    'name':"weiboc0001@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5bce9d95f5c8ba0034dbbb4eafafe15219"
    }]

account[Usages.Network] = [{
                              'name':"weiboc0005@163.com",
                              'password': "1a2b3c"
                              # 'gsid':"3_5bce9d95f5c8ba0034dbbb4eafafe15219"
                          }]

account[Usages.UpdateInfo] = [{
    'name':"weiboc000005@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afe4ad66c8dba199459ad204524bf0792"
    }]

account[Usages.FetchWeibo] = [
    {
    'name':"weiboc0005@163.com",
    'password': "1a2b3c"
    # 'gsid':"4ue42ba21PBiLPFiPOWxAdorHed"
    },
    {
    'name':"weiboc0006@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afd406aa5d926287c9586b590b6240626"
    },
    {
    'name':"weiboc0007@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afd406aa5d0e0300d4486f88b438a7752"
    },
    {
    'name':"weiboc0008@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afd406aaabe8873c9ed9183e6b0e5d89c"
    },
    {
    'name':"weiboc0009@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afd406b93018fc462512368d4b456cf6f"
    },
    {
    'name':"weiboc0010@163.com",
    'password': "1a2b3c"
    # 'gsid':"3_5afd406b93005c204a6458ef7bf752db4d"
    },
    {
    'name':"weiboc0012@163.com",
    'password': "1a2b3c"
    # 'gsid':"4u9qCpOz1LhWCn4Gh6vRGduyk8V"
    }
    ]



