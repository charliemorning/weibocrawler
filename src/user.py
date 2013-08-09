# -*- coding: UTF-8 -*-
'''
#=============================================================================
#     FileName: user.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:53
#      History:
#=============================================================================
'''


# from global_.util import get
from net import weibo_get
from log import logger


from config import BaseURL, WeiboLimitDate
from parse.extract import (parseCountStats,
    # parseFansPageInfo,
    parseFollowsPageInfo,
    parseFollowsListOnePage,
    parseWeiboPageInfo,
    # parseFansListOnePage,
    parseWeibosListOnePage,
    parseUserID,
    parseUserGenInfo,
    parseAuthType,
    )

import re
import pdb
import datetime
import exceptions
from mongoengine import *
import pymongo

class Comment(EmbeddedDocument):

    pass


class User(Document):

    uid = StringField(name='uid', default=None, verbose_name=u'user ID')
    domain = StringField(name='domain', primary_key=True, verbose_name=u'user primary key')

    auth = StringField(name='auth', default=None, verbose_name=u'authority')
    nickname = StringField(name='nickname', default=None, verbose_name=u'nikename')
    sex = StringField(name='sex', default=None, verbose_name=u'sex')
    area = StringField(name='area', default=None, verbose_name=u'area')
    birthday = DateTimeField(name='birthday', verbose_name=u'birthday')
    auth_info = StringField(name='auth_info', verbose_name=u'authorized information')
    desc = StringField(name='desc', verbose_name=u'description')

    fans = ListField(field=StringField(max_length=255), name='fans', verbose_name=u'fans list')
    follows = ListField(field=StringField(max_length=255), name='follows', verbose_name=u'follows list')


    fansCnt = IntField(name='fansCnt', verbose_name=u'fans count')                
    followCnt = IntField(name='followCnt', verbose_name=u'follows count')            
    weiboCnt = IntField(name='weiboCnt', verbose_name=u'weibos count')              

    informative = BooleanField(name='informative', default=True, verbose_name=u'if it is informative')

    authType = StringField(name='authType', default='', verbose_name=u'type of authority')

    locked = BooleanField(name='locked', default=False, verbose_name=u'if it is locked')
    holder = StringField(name='holder', verbose_name=u'current document holder')

    createTime = DateTimeField(name='createTime', verbose_name=u'create time in database')
    updateTime = DateTimeField(name='updateTime', verbose_name=u'update time in database')

    infoFetched = BooleanField(name='infoFetched', default=False, verbose_name=u'if information fetched')

    infoHTML = StringField(name='infoHTML', verbose_name=u'original html code')
    unrecognizedInfo = BooleanField(name='unrecognizedInfo', verbose_name=u'if it is unrecognizable')

    followFetched = BooleanField(name='followFetched', default=False, verbose_name=u'if followed fetched')
    followsUpdateTime = DateTimeField(name='followsUpdateTime', verbose_name=u'time when update the follows')
    followUpdateHistory = ListField(field=DateTimeField(name='followUpdateTimeRecord'), name='followUpdateHistory', verbose_name=u'record of time when update the follows')


    weibos = ListField(field=StringField(max_length=255), name='weibos', verbose_name=u'list of weibos')
    weiboFetched = BooleanField(name='weiboFetched', default=False, verbose_name=u'if weibo fetched')
    weiboUpdateTime = DateTimeField(name='weiboUpdateTime', verbose_name=u'time when update the weibo')
    weiboUpdateHistory = ListField(field=DateTimeField(name='weiboUpdateTimeRecord'), name='weiboUpdateHistory', verbose_name=u'record of time when update the weibo')

    def lock(self, holder):

        self.locked = True
        self.holder = holder
        self.save()

    def unlock(self):

        self.locked = False
        self.holder = 'free'

        try:
            self.save()
        except pymongo.errors.AutoReconnect:
            d = {'object': self.domain, 'extra': ''};logger.info(u'begin to fetch%s', name, extra=d)

    def save(self, *args, **kwargs):

        now = datetime.datetime.now()

        if User.objects.all().filter(domain=self.domain).count() == 0:
            self.createTime = now
        self.updateTime = now

        super(User, self).save()

    def save_by_followcrawler(self, *args, **kwargs):

        now = datetime.datetime.now()
        
        self.followsUpdateTime = now
        self.followFetched = True
        self.followUpdateHistory.append(now)

        self.save()

    def save_by_infocrawler(self, *args, **kwargs):

        now = datetime.datetime.now()

        self.infoFetched = True
        self.infoUpdateTime = now

        self.save()

    def save_by_weibocrawler(self, *args, **kwargs):

        now = datetime.datetime.now()

        self.weiboFetched = True
        self.weiboUpdateTime = now
        self.weiboUpdateHistory.append(now)

        self.save()

    def getUserStats(self, fresh=False, **kwargs):
        """
        to get the count of follows fans and weibos
        """

        if fresh:
            mainPage = weibo_get(self.domainURL(), 5, **kwargs)
            cnt = parseCountStats(mainPage)
        else:
            cnt = (len(User.objects.get(id=self.id).follows),
                len(User.objects.get(id=self.id).fans),
                len(User.objects.get(id=self.id).weibo),
                )

        return cnt

    def fetchUserStats(self, fresh=True, **kwargs):
        """
        to get the statistic information of user
        """

        stats = self.getUserStats(fresh, **kwargs)
        self.followsCnt = stats[0]
        self.fansCnt = stats[1]
        self.weiboCnt = stats[2]

        return (self.followCnt, self.fansCnt, self.weiboCnt,)

    def fetchAuthType(self, **kwargs):

        mainPage = weibo_get(self.domainURL(), 5, **kwargs)
        self.authType = parseAuthType(mainPage)

        return self.authType

    def getID(self):
        if self.uid is None:
            self.fetchMyID()

        return self.uid

    def getDomain(self):
        if self.domain is None:
            pass

        return self.domain

    def domainURL(self):
        """
        to get the main url of user
        no domain if user id ends with 10
        """
        p = re.compile(r'^\d{10}$')
        if re.match(p, self.domain):
            u = 'u/'
        else:
            u = ''
        return '{0}{1}{2}'.format(BaseURL, u, self.domain)

    def IDURL(self):
        """
        get main page url by id
        """

        return '{0}{1}'.format(BaseURL, self.uid)

    def fetchMyID(self, **kwargs):
        """
        to get id by url
        """
        mainPage = weibo_get(self.domainURL(), 5, **kwargs)
        idStr = parseUserID(mainPage)
        self.uid = idStr

    def fetchMyInfo(self, **kwargs):
        """
        to get basic information of user
        nick name
        authority
        sex
        area
        birthday
        information of authority
        description
        """
        mainPage = self.getProfilePage(**kwargs)

        self.infoHTML = mainPage

        try:
            info = parseUserGenInfo(mainPage)
        except:
            pass
            self.unrecognizedInfo = True
        else:

            self.nickname = info[0]
            self.auth = info[1]
            self.sex = info[2]
            self.area = info[3]
            self.birthday = info[4] if info[4] is not None else '1900-01-01'
            self.auth_info = info[5]
            self.desc = info[6]

            self.unrecognizedInfo = False

    def __getUsersPage(self, type, **kwargs):
        """
        to get the page user
        called by getProfilePage, getFollowersPage, getFansPage
        """
        url = '{0}{1}/{2}'.format(BaseURL, self.uid, type)
        response = weibo_get(url, 5, **kwargs)

        return response.read()  

    def getProfilePage(self, **kwargs):
        """
        information page
        """
        return self.__getUsersPage('info', **kwargs)

    def getFollowsPage(self, **kwargs):
        """
        follow page
        """
        return self.__getUsersPage('follow', **kwargs)

    def getFansPage(self, **kwargs):
        """
        fans page

        not used yet
        """
        return self.__getUsersPage('fans', **kwargs)

    def getWeiboPage(self, **kwargs):
        """
        weibo page
        """
        response = weibo_get(self.domainURL(), 5, **kwargs)
        return response.read()

    def __getPaged_pattern(self, name, _prHandler, _piParser, _pParser, _proc, _stop=None, **kwargs):
        """
        this is a pattern with which to fetch the paged information of user
        it is used when fetching followers, fans, and weibos
        @param name
        @param _prHandler
        @param _piParser
        @param _pParser
        @param _proc
        @param _stop
        @param kwargs
        """

        d = {'object': self.domain, 'extra': ''};logger.info(u'fetch%s', name, extra=d)

        _list = []

        # to get the first page
        _firstP = _prHandler(**kwargs)

        # import pdb;pdb.set_trace()

        try:
            # to parse the page information
            _pInfo = _piParser(_firstP)

        except:

            pass

        else:
            # to parse the current index of page and total pages
            _i, _t = int(_pInfo[0]), int(_pInfo[1])


            for i in xrange(_i, _t):

                d = {'object': self.domain, 'extra': ''};logger.info(u'page: %d/%d', i, _t, extra=d)

                # request the page
                _p = _prHandler(page=str(i), **kwargs)

                # tp parse the page
                _l = _pParser(_p)

                _list += [_proc(e) for e in _l]

                # to check if a stopper is passed
                if _stop:

                    # to check if current state meets the stop
                    if len(_l) > 0 and _stop(_l):
                        d = {'object': self.domain, 'extra': ''};logger.info(u'stop condition meets!', extra=d)
                        break

        finally:
            return _list

    def getFollows(self, **kwargs):

        return self.__getPaged_pattern(u'关注者', lambda **kwargs:self.getFollowsPage(**kwargs), parseFollowsPageInfo,
            parseFollowsListOnePage, lambda e:User(fans=[self.getDomain()], domain=e[0], nickname=e[1]), **kwargs)

    def __weibo_time_limit(self, l):

        # to get the last weibo in the list
        w = l[-1]
        time = w[5]

        format = '%Y-%m-%d %X'
        try:
            dt = datetime.datetime.strptime(str(time), format)
        except exceptions.Exception as e:
            print e
        else:

            if dt < WeiboLimitDate:
                return True
            else:
                return False

    def getWeibos(self, **kwargs):
        """
        to get all weibo of one user
        """

        return self.__getPaged_pattern(u'微博', lambda **kwargs:self.getWeiboPage(**kwargs), parseWeiboPageInfo,
            parseWeibosListOnePage, lambda e:Weibo(wid=e[0], html=e[1], text=e[2], isRepost=e[3], category=e[4], postTime=e[5], client=e[6], user=self),
            self.__weibo_time_limit, **kwargs)

    def getFans(self):
        pass


class Weibo(Document):

    wid = StringField(name='wid', primary_key=True, verbose_name=u'微博主码')

    html = StringField(name='html', verbose_name=u'原始的html代码片段')

    text = StringField(name='text', default=None, verbose_name=u'原始的html代码片段')

    isRepost = BooleanField(name='isRepost', verbose_name=u'是否为转发微博')

    postTime = DateTimeField(name='postTime', verbose_name=u'发布的时间')

    createdTime = DateTimeField(name='createdTime', verbose_name=u'数据库创建微博时间')
    updateTime = DateTimeField(name='updateTime', verbose_name=u'数据库更新微博时间')

    client = StringField(name='client', verbose_name=u'客户端')

    category = StringField(name='category', verbose_name=u'微博类型')

    comments = ListField(field=GenericEmbeddedDocumentField(), name='comments', verbose_name=u'评论列表')

    commentFetched = BooleanField(name='commentFetched', default=False, verbose_name=u'是否已经获取评论')
    commentUpdateTime = DateTimeField(name='commentUpdateTime',  verbose_name=u'获取评论时间')
    commentUpdateHistory = ListField(field=DateTimeField(name='commentUpdateTimeRecord'), default=[], name='commentUpdateHistory', verbose_name=u'评论更新时间记录')


    user = ReferenceField(User, reverse_delete_rule=DO_NOTHING, verbose_name=u'微博作者')

    def save(self, *args, **kwargs):
        """
        """
        now = datetime.datetime.now()

        if Weibo.objects.all().filter(wid=self.wid).count() == 0:
            self.createdTime = now
            
        self.updateTime = now

        super(Weibo, self).save()

    def save_by_weibocrawler(self, *args, **kwargs):
        """
        """

        self.save()