# -*- coding: UTF-8 -*-
"""
#=============================================================================
#     FileName: parse.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:53
#      History:
#=============================================================================
"""


import re
import pdb
import time
import datetime
import exceptions

import chardet

from extern.BeautifulSoup import BeautifulSoup

from parse.parse_page import (
    MainPage,
    FFPage,
    FollowPage,
    FanPage,
    )

from parse.parse_exception import (
    PagePartNotFoundException,
    UserIDNotFound,
    )

def regSearch(pattern, text):
    """
    使用正则表达式匹配目标
    """
    compiledPattern = re.compile(pattern, re.X)
    result = re.search(compiledPattern, text)
    
    return result


def extract_gsid(cookieFile):
    """
    to extract the gsid in cookie file
    """

    lines = cookieFile.split("\n")

    gsid = [l for l in lines if l is not u""][-1].split("\t")[-1]

    if gsid.endswith("\r"):
        gsid = gsid[:-1]
    return gsid
    

def extractPwdName(text):
    """
    解析登陆密码的请求参数中密码的随机生成码
    """
    pwdName = "password"
    pattern = r"password_(\d+)"
    
    number = regSearch(pattern, text)

    if number is None:
        err_msg = "failto parse pwd name.\n"
        raise exceptions.Exception(err_msg)
    pwdName += "_" + number.group(1)
        
    return pwdName


def extractVKValue(text):
    """
    解析登陆时需要的vk参数
    """
    
    vk = ""
    
    pattern = r'(\w{4})_(\w{4})_(\w{10})'
    
    value = regSearch(pattern, text)
    
    if value is None:
        err_msg = "failto parse VK value.\n"
        raise exceptions.Exception(err_msg)

    vk += value.group(1) + "_" + value.group(2) + "_" + value.group(3)
        
    return vk

def extractLoginRedirectionURL(text):
    """
    解析登陆请求过后返回的重定向页面中的重定向URL
    """
    # import pdb;pdb.set_trace()
    soup = BeautifulSoup(text)
    
    tag = "a"
    attr = ""
    value = ""
    all_a = soup.findAll(tag)
    
    if all_a is None:
        err_msg = "failto parse redirect URL after login."
        raise exceptions.Exception(err_msg)
    
    target = None
    
    for a in all_a:
        if a.text == u"点击这里":
            target = a['href']
            break
        
        
    return target

def parseUserID(text):
    """
    分析用户的用户id
    @raise PagePartNotFoundException: 当没有找到用户概要信息时，抛出此异常
    """

    p = MainPage(text)

    try:
        DOM = p.generalInfoPart()
    except PagePartNotFoundException as e:
        raise
    else:

        tag2 = "a"
        attr2 = ""
        value2 = ""
        soup2 = BeautifulSoup(str(DOM))
        a = soup2.find("a")
    
        if a is None:
            raise UserIDNotFound()

        urlParts = a["href"].split("/")

        return urlParts[1]


def parseUserGenInfo(text):
    """
    解析用户基本信息
    """


    try:
    
        s = lambda tag, t: regSearch(r'{0}[:|：](.*?)<br'.format(tag), t)

        f = lambda x: x.group(1) if x is not None else None

        e = lambda tag, t: f(s(tag, t))
        
        chd = lambda s: chardet.detect(s)

        nn = e('昵称', text)

        auth = e('认证', text)

        sex = e('性别', text)

        area = e('地区', text)

        desc = e('简介', text)

        bd = e('生日', text)

    
        format = '%Y-%m-%d'
        bd = datetime.datetime(1900, 01, 01) if bd is None else datetime.datetime.strptime(bd, format)

    except (ValueError):

        bd = datetime.datetime(1900, 01, 01)
        
    finally:

        auth_info = e('认证信息', text)
        if auth_info is not None:
            ch = chd(auth_info)
            auth_info = auth_info.decode(ch['encoding'])


        return (str(nn).encode('UTF-8'),
            str(auth).encode('UTF-8'),
            str(sex).encode('UTF-8'),
            str(area), bd,
            str(auth_info).encode('UTF-8'),
            str(desc).encode('UTF-8'),)

def parseCountStats(text):
    """
    解析用户关注，粉丝和微博的数量
    @raise PagePartNotFoundException: 当没有找到用户概要信息的页面部分时，抛出此异常
    @raise UserCountStatParseError: 当没有解析到用户的数量信息时，抛出此异常
    """

    p = MainPage(text)

    try:
        divText = p.generalInfoPart()
    except PagePartNotFoundException as e:
        raise
    else:

        flc_p = ur'关注\[(\d+)\]'
        fnc_p = ur'粉丝\[(\d+)\]'
        wc_p = ur'微博\[(\d+)\]'



        flc = regSearch(flc_p, divText.text)
        fnc = regSearch(fnc_p, divText.text)
        wc = regSearch(wc_p, divText.text)

        if flc is None or fnc is None or wc is None:
            raise UserCountStatParseError()

        return (flc.group(1), fnc.group(1), wc.group(1),)

def parseAuthType(text):
    """
    解析用户的认证类型
    @raise PagePartNotFoundException: 当没有找到用户概要信息的页面部分时，抛出此异常
    """

    p = MainPage(text)
    try:
        authText = p.authTypePart()
    except PagePartNotFoundException as e:
        raise
    else:
        vt_p = r'http://u1.sinaimg.cn/upload/2011/07/28/(\d{4}).gif'
        vt = regSearch(vt_p,  str(authText))

        if vt is None:
            return '无认证'
        else:
            if vt.group(1) == '5338':
                return u'认证个人'
            elif vt.group(1) == '5337':
                return u'公共页面'
            else:
                return u'无法识别'

def __parse_page_info(p):
    """
    解析页面上的分页信息;主要用于
    """

    try:
        paginText = p.getPagination()
    except PagePartNotFoundException as e:
        raise
    else:

        pattern = ur"(\d+)/(\d+)页"

        result = re.search(pattern, paginText)

        # result = regSearch(pattern, paginText.encode("UTF-8"))
    
        if result is None:
            err_msg = "failto parse page info.\n"
            raise exceptions.Exception(err_msg)

        #group(1)为当前页;group(2)为总页数
        return result.group(1), result.group(2)



def parseFansPageInfo(text):
    """
    解析用户的粉丝页面分页信息
    """
    p = FanPage(text)
    return __parse_page_info(p)

def parseFollowsPageInfo(text):
    """
    解析用户的跟随者页面分页信息
    """
    p = FollowPage(text)
    return __parse_page_info(p)

def parseWeiboPageInfo(text):
    """
    解析用户微博页面分页信息
    """
    p = MainPage(text)
    return __parse_page_info(p)

    
def parseWeiboUserDomain(urlStr):
    """
    从url连接中获取用户的domain
    """
    firstHalf = urlStr.split("?")

    urlParts = firstHalf[0].split("/")
    if urlParts[-1] == "":
        return urlParts[-2]
    else:
        return urlParts[-1]



def parseOneFanFromFansList(text):
    """
    从某个用户的粉丝列表中解析一个粉丝的信息
    @return {tuple} ()
    """
    
    user = ()
    soup = BeautifulSoup(text)
    
    tag = "a"
    attr = ""
    value = ""
    all_a = soup.findAll("a")
    
    if all_a is None:
        err_msg = "failto find one fan/follow.\n"
        raise exceptions.Exception(err_msg)#WeiboFanFollowSearchError(err_msg, text, tag, attr, value)
    
    urlStr = all_a[0]["href"]

    domain = parseWeiboUserDomain(urlStr)
    
    name = all_a[1].text
    
    return (domain, name,)



def __parse_ff_list(p):
    """
    解析一个用户的一页粉丝或者关注的人，返回一个列表
    被parseFansList和parseFollowsList调用
    @raise PagePartNotFoundException: 当找不到粉丝或者跟随者列表的时候，抛出此异常
    """
    userGenInfoList = []


    try:
        ffDomList = p.oneFFListPart()
    except PagePartNotFoundException as e:
        raise
    else:
    
        for ffTable in ffDomList:
            try:
                userGenInfo = parseOneFanFromFansList(str(ffTable))
            except e:
                continue
            
            userGenInfoList.append(userGenInfo)

        return userGenInfoList

def parseFollowsListOnePage(text):
    """
    解析一个用户一页的跟随者，返回一个列表
    """
    p = FollowPage(text)
    return __parse_ff_list(p)

def parseFansListOnePage(text):
    """
    解析一个用户一页的粉丝，返回一个列表
    """
    p = FanPage(text)
    return __parse_ff_list(p)



def parseWeiboItemID(piece):
    """
    提取微博ID
    @return: 如果提取到，则返回微博Id，否则返回None
    """
    pattern = r'id="(\w_\w+)"'
    
    weiboId = regSearch(pattern, piece)

    if weiboId is None:
        
        return None

    return weiboId.group(1)

def isRepostTextWeibo(piece):
    """
    判断是否是转发的文字微博
    """
    soup = BeautifulSoup(piece)
    
    span = soup.find("span", {"class": "cmt"})
    
    if span is None:
        return False

    return True if "转发了" in span.text else False



def __parse_text_from_weibo_piece(piece):
    """
    解析微博内容
    @
    """
    try:
        text = MainPage.weiboTextPart(piece)
    except PagePartNotFoundException as e:
        raise
    else:
        return text


def parsePureTextWeiboContent(piece):
    """
    解析纯文字微博的内容
    
    """
    try:
        text = __parse_text_from_weibo_piece(piece)
    except PagePartNotFoundException as e:
        raise
    else:
        return text
    
def parseImageWeiboContent(piece):
    """
    解析转发的文字微博的内容
    @
    """
    try:
        text = __parse_text_from_weibo_piece(piece)
    except PagePartNotFoundException as e:
        raise
    else:
        return text


def parseRepostTextWeiboContent(piece):
    """
    解析转发的文字微博的内容
    @
    """
    try:
        text = __parse_text_from_weibo_piece(piece)
    except PagePartNotFoundException as e:
        raise
    else:
        return text

def parseRepostImageWeiboContent(piece):
    """
    解析转发的带图片的微博的内容
    @raise WeiboContentTextSearchError: 当解析微博正文出错的时候，抛出此异常
    """
    try:
        text = __parse_text_from_weibo_piece(piece)
    except PagePartNotFoundException as e:
        raise
    else:
        return text


def __parse_original_user_from_repost_weibo(piece):
    """
    提取转发微博当中的作者信息
    #TODO Fixme
    """
    soup = BeautifulSoup(piece)
    
    a = soup.findAll("a")
    
    user = WeiboUser()
    
    user.domain = parseWeiboUserID(a[1]["href"], True)
        
    user.currentName = a[1].text
    
    return user

def parseOringinalUserFromRepostTextWeibo(piece):
    """
    解析
    #TODO Fixme
    """
    return __parse_original_user_from_repost_weibo(piece)

def parseOriginalUserFromRepostImageWeibo(piece):
    """
    #TODO Fixme
    """
    return __parse_original_user_from_repost_weibo(piece)

def get_current_year():
    """
    获得当前的年份
    """
    return time.localtime().tm_year

def timestamp_2_formatdate(timestamp):
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    return time.strftime(ISOTIMEFORMAT, time.localtime(timestamp))


def minutes_2_timestamp(minutes):
    """
    给定一定的分钟数，得到这么多分钟之前的时间戳
    """
    
    seconds = int(minutes) * 60
    
    currentTime = time.time()
    
    return currentTime - seconds


def timepoint_to_timestamp(hours, minutes):
    """
    给定一个时间点，把其转换为那个时刻的时间戳
    年月日为当前年月日
    """
    hours = int(hours)
    minutes = int(minutes)
    
    
    timeTuple = time.localtime()
    
    currentHour = timeTuple[3]
    
    currentMinutes = timeTuple[4]
    
    if currentMinutes < minutes:
        currentHour -= 1
        currentMinutes += 60
        
    totalMinutes = (currentHour - hours) * 60 + currentMinutes - minutes
    totalSeconds = totalMinutes * 60
    
    return time.time() - totalSeconds


def get_date_format(year, month, day, hour, minute, second="00"):
    """
    把年月日转换为固定的格式
    """
    return "%s-%s-%s %s:%s:%s" %(str(year), str(month), str(day), str(hour), str(minute), str(second))



def __parse_weibo_time_0x01(text):
    """
    如果是       **分钟前
    """
    pattern = ur"(\d{1,2})分钟前"
    c = re.compile(pattern)
    result = re.search(c, text)

    if result is None:        
        return None

    minutes = result.group(1)
    
    timestamp = minutes_2_timestamp(minutes)
    
    return timestamp_2_formatdate(timestamp)



def __parse_weibo_time_0x02(text):
    """
    如果是       今天 **:**
    @return 如果不匹配则返回None
    """
    pattern = ur"今天 ([0-2][0-9]):([0-5][0-9])"
    c = re.compile(pattern)
    result = re.search(c, text)

    if result is None:
        return None
    
    hours = result.group(1)
    minutes = result.group(2)
    timestamp = timepoint_to_timestamp(hours, minutes)
    return timestamp_2_formatdate(timestamp)

def __parse_weibo_time_0x03(text):
    """
    如果是 **月**日 **:**
    @return 如果不匹配则返回None
    """
    pattern = ur"([0-1][0-9])月([0-3][0-9])日 ([0-2][0-9]):([0-5][0-9])"
    c = re.compile(pattern)
    result = re.search(c, text)

    if result is None:
        return None
    
    month = result.group(1)
    day = result.group(2)
    hour = result.group(3)
    minute = result.group(4)
    year = get_current_year()
    return get_date_format(year, month, day, hour, minute)

def __parse_weibo_time_0x04(text):
    """
    如果是 yyyy-mm-dd hh:mm:ss
    """

    pattern = ur"(\d{4})-([0-1][0-9])-([0-3][0-9]) ([0-2][0-9]):([0-5][0-9]):([0-5][0-9])"
    c = re.compile(pattern)
    result = re.search(c, text)

    if result is None:
        return None

    year = result.group(1)
    month = result.group(2)
    day = result.group(3)
    hour = result.group(4)
    minute = result.group(5)
    second = result.group(6)
    return get_date_format(year, month, day, hour, minute, second)



def str2datetime(formattedStr, format):
    
    return datetime.datetime.strptime(formattedStr, format)

def parseWeiboTime(text):
    """
    解析微博发表的时间
    @return 如果不匹配则返回None
    """

    # pdb.set_trace()
    format = '%Y-%m-%d %X'

    timestamp = __parse_weibo_time_0x01(text)

    if timestamp is not None:
        return str2datetime(timestamp, format)

    
    timestamp = __parse_weibo_time_0x02(text)
    if timestamp is not None:
        return  str2datetime(timestamp, format)
    
    timestamp = __parse_weibo_time_0x03(text)
    if timestamp is not None:
        return  str2datetime(timestamp, format)

    timestamp = __parse_weibo_time_0x04(text)
    if timestamp is not None:
        return  str2datetime(timestamp, format)
    
    raise exceptions.Exception("failto parse time.")
    

def parseWeiboClient(text):
    """
    解析微博的客户端
    @raise exceptions.Exception: 当没有解析到客户端信息的时候，抛出此异常
    """
    
    pattern = u"来自([\u4e00-\u9fa5a-zA-Z0-9]+)"
    c = re.compile(pattern)
    result = re.search(c, text)
    
    if result is None:
        raise exceptions.Exception("failto parse client.")
    
    return result.group(1)

def parseWeiboTimeAndClientText(piece):
    """
    解析微博发表的时间和客户端
    @raise PagePartNotFoundException: 当没有解析到客户端信息的时候，抛出此异常
    """

    try:
        text = MainPage.timeAndClientPart(piece)
    except PagePartNotFoundException as e:
        # 如果没有找到时间和客户端的html代码
        raise
    else:
        return text

def parseWeiboItem(piece):
    """
    解析一条微博信息
    @raise PagePartNotFoundException
    """

    try:
        all_div = MainPage.weiboBodyPart(piece)
    except PagePartNotFoundException as e:
        raise

    
    first_div = all_div[1]
    first_div_str = str(first_div)
    
    # 时间信息和客户端
    timeClientPart = None
    
    # 文字微博，只有两个div
    if len(all_div) == 2:
        
        # 解析纯文本微博的内容
        try:
            weiboContent = parsePureTextWeiboContent(first_div_str)
        except PagePartNotFoundException as e:
            
            raise

        isRepost = False
        cate = 1
        
        # time information is in the first div
        timeClientPart = first_div_str

    #有可能是转发文字微博，也有可能是图片微博
    elif len(all_div) == 3:
        
        #如果是转发的文字微博
        if isRepostTextWeibo(first_div_str):
            
            #解析微博原作者的信息
            #originalUser = parseOringinalUserFromRepostTextWeibo(first_div_str)

            #获取微博征文
            try:
                orininalText = parseRepostTextWeiboContent(first_div_str)
            except PagePartNotFoundException as e:
                
                raise
            
            isRepost = True
            cate = 2

        #否则是图片微博
        else:

            #获取微博正文
            try:
                weiboContent = parseImageWeiboContent(first_div_str)
            except PagePartNotFoundException as e:
                raise

            text = weiboContent
            isRepost = True
            
            cate = 3

        second_div = all_div[2]
        second_div_str = str(second_div)

        # time information is in the first div
        timeClientPart = second_div_str
        

    #转发的图片微博
    elif len(all_div) == 4:
        
        #originalUser = parseOriginalUserFromRepostImageWeibo(first_div_str)

        #解析微博转发的图片微博的正文
        try:
            weiboContent = parseRepostImageWeiboContent(first_div_str)
        except PagePartNotFoundException as e:
            raise



        isRepost = True
        cate = 4


        third_div = all_div[3]
        third_div_str = str(third_div)

        # time information is in the first div
        timeClientPart = third_div_str
        
        
    #获取微博发布时间和使用的客户端
    try:
        # FIXME
        #解析有时间和客户端信息的文字片段
        clientTimeSnippet = parseWeiboTimeAndClientText(timeClientPart)
        
        #获取时间信息
        try:
            time = parseWeiboTime(clientTimeSnippet)
        except Exception as e: # FIXME
            print e
            time = datetime.datetime(1900, 01, 01)
        
        #获取客户端信息
        try:
            client = parseWeiboClient(clientTimeSnippet)
        except :
            client = None
            
    except :# FIXME
        time = datetime.datetime(1900, 01, 01)
        client = None




    return (weiboContent, isRepost, str(cate), time, client,)





def parseWeibosListOnePage(text):
    """
    解析一个用户一页的微博，返回一个列表
    """
    p = MainPage(text)

    all_c = p.weiboListPart()
      
    weiboItemResults = []
    for c in all_c:

        originHTML = str(c)
        
        # 解析每条微博的id
        weiboID = parseWeiboItemID(originHTML)
            

        # 没有找到微博ID，则认为不是可用的微博信息
        # 如果提取到的是微博正文
        if weiboID is not None:

            #解析微博的作者，内容，是否转发
            try:
                weibo = parseWeiboItem(originHTML)
            except:
                continue

            weibo = (weiboID, originHTML,) + weibo
            
            weiboItemResults.append(weibo)


    return weiboItemResults