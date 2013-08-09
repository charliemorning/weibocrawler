# -*- coding: UTF-8 -*-
"""
#=============================================================================
#     FileName: network.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:24
#      History:
#=============================================================================
"""

from net import login
from parse.extract import extract_gsid
from user import User
from config import *
from log import logger

import mongoengine

import pdb
import time

from task import FollowsTask, WeiboTask, BuildNetworkTask, UpdateInfoTask


class Network:
    """
    """

    def __init__(self):
        """
        """
        self.doWhat = Usage

        mongoengine.connect(Database['name'], host=Database['host'])

        self.name = account[Usage][SEQ]['name']
        self.password = account[Usage][SEQ]['password']
        # self.gsid = account[Usage][SEQ]['gsid']

    def get_gsid(self):
        """
        this must be used after login
        """
        path = Cookies.LoginCookieFile

        f = codecs.open(path, "rb","UTF-8")
        content = f.read()
        f.close()

        return extract_gsid(content)

    def setFollowCrawlerAccountInfo(self):
        """
        """
        pass

    def setInfoCrawlerAccount(self):
        """
        """
        pass
       
    def makeSeed(self):

        if len(User.objects()) != 0:
            return

        user = User()

        user.uid = '1197161814'
        user.domain = '1197161814'
        user.locked = False

        user.save()

    def __fetch_follows(self):

        self.makeSeed()

        while True:

            usersQuerySet = User.objects(uid__ne=None, locked=False, followFetched=False)

            if usersQuerySet.count() == 0:
                print u'暂时没有需要获取的关注者'
                time.sleep(10)
                continue

            u = usersQuerySet[0]

            task = FollowsTask(u, self.gsid)

            task.start()
            task.join()







    def __update_info(self):

        while True:

            usersQuerySet = User.objects(locked=False, infoFetched=False)

#            pdb.set_trace()

            if usersQuerySet.count() == 0:
                print u'暂时没有需要更新的用户'
                time.sleep(10)
                continue


            u = usersQuerySet[0]

            d = {'object': u.domain, 'extra': ''};logger.info(u'更新用户信息', extra=d)

            task = UpdateInfoTask(u, self.gsid)

            task.start()
            task.join()



    def __fetch_fans(self):
        pass

    def __fetch_weibos(self):

        while True:

            usersQuerySet = User.objects(uid__ne=None, locked=False, weiboFetched=False)

            # pdb.set_trace()

            if usersQuerySet.count() == 0:
                print u'暂时没有需要获取的微博'
                time.sleep(10)
                continue

            u = usersQuerySet[0]

            task = WeiboTask(u, self.gsid)

            task.start()
            task.join()

    def __update_center_user(self):

        users = User.objects.filter(uid='1197161814')

        user = users[1]
        

        # to get follower's id list
        fids = user.follows

        for fid in fids:

            
            users = User.objects.filter(uid=fid, locked=False, weiboFetched=False)
            if users.count() == 0:
                continue


            d = {'object': fid, 'extra': ''};logger.info(u'当前用户', extra=d)

            user = users[0]
            
            weibos = user.getWeibos(vt='4', gsid=self.gsid)

            user.weibos += [w.wid for w in weibos]

            user.save_by_weibocrawler()

            for w in weibos:
                w.save_by_weibocrawler()

    def __build_network(self):

        while True:

            usersQuerySet = User.objects(uid__ne=None, locked=False, followFetched=False)

            if usersQuerySet.count() == 0:
                print u'暂时没有需要获取的关注者'
                time.sleep(10)
                continue

            u = usersQuerySet[0]

            task = BuildNetworkTask(u, self.gsid)

            task.start()
            task.join()



    def run(self):

        login(self.name, self.password)

        self.gsid = self.get_gsid()

        print self.gsid

        pdb.set_trace()

        if self.doWhat == Usages.FetchFollows:
            self.__fetch_follows()

        elif self.doWhat == Usages.UpdateInfo:
            self.__update_info()

        elif self.doWhat == Usages.FetchWeibo:
            self.__fetch_weibos()

        elif self.doWhat == Usages.Center:
            self.__update_center_user()
        elif self.doWhat == Usages.Network:
            self.__build_network()
        else:
            pass





