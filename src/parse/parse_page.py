"""
#=============================================================================
#     FileName: parse_page.py
#         Desc: There are several kind of pages and each kind of page as follow:
#                1) login page
#                2) main page of user
#                    a) general information part
#                    b) weibo list part
#                    c) pageination part
#                3) follow page
#                4) fans page
#                5) information page
#                6) comment page
#                7) repost page
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:53
#      History:
#=============================================================================
"""
# -*- coding: UTF-8 -*-

import re
import pdb
from extern.BeautifulSoup import BeautifulSoup
from parse.parse_exception import PagePartNotFoundException


class Page:

    def __init__(self, text):
        self.text = text
        self.soup = BeautifulSoup(self.text)

    def getSoup(self):
        return self.soup

class PaginatedPage(Page):

    def __init__(self, text):
        Page.__init__(self, text)

    def getPagination(self):
        """
        提取页面分页信息
        @raise PagePartNotFoundException: 当没有找到概要信息的页面部分时，抛出此异常
        """
        tag = "div"
        attr = "id"
        value = "pagelist"
        div = self.soup.find(tag, {attr: value})

        if div is None:
            raise PagePartNotFoundException()

        return div.text

class MainPage(PaginatedPage):
    """
    """

    def __init__(self, text):
        PaginatedPage.__init__(self, text)

    def generalInfoPart(self):
        """
        提取用户概要信息的页面部分
        @raise PagePartNotFoundException: 当没有找到概要信息的页面部分时，抛出此异常
        """
        tag = "div"
        attr = "class"
        value = "tip2"
        # pdb.set_trace()
        divDOM = self.soup.find(tag, {attr: value})

        if divDOM is None:
            raise PagePartNotFoundException()

        return divDOM

    def authTypePart(self):
        """
        认证信息在概要信息里面，先调用generalInfoPart
        @raise PagePartNotFoundException: 当没有找到概要信息的页面部分时，抛出此异常
        """

        #div = self.generalInfoPart()
        

        tag = "div"
        attr = "class"
        value = "ut"

        authDivDOM = self.soup.find(tag, {attr: value})

        if authDivDOM is None:
            raise PagePartNotFoundException()

        return authDivDOM

    def weiboListPart(self):
        """
        提取微博的列表部分
        @raise PagePartNotFoundException: 当没有找到微博列表信息的页面部分时，抛出此异常
        """

        tag = "div"
        attr = "class"
        value = "c"
        all_c = self.soup.findAll(tag, {attr: value})

        if all_c is None:
            raise PagePartNotFoundException()

        return all_c


    @staticmethod
    def weiboTextPart(text):
        """
        """

        s = BeautifulSoup(text)

        tag = "span"
        attr = "class"
        value = "ctt"
        span = s.find(tag, {attr: value})

        if span is None:
            raise PagePartNotFoundException()

        return span.text

    @staticmethod
    def timeAndClientPart(text):
        """
        """

        s = BeautifulSoup(text)
    
        tag = "span"
        attr = "class"
        value = "ct"
        
        span = s.find(tag, {attr: value})
        
        # 如果没有找到时间和客户端的html代码
        if span is None:
            raise PagePartNotFoundException()
    
        return span.text

    @staticmethod
    def weiboBodyPart(text):
        """
        """
        s = BeautifulSoup(text)
        tag = "div"
        attr = ""
        value = ""
        divDOMs = s.findChildren(tag)
        
        if divDOMs is None:
            err_msg = "fail to parse weibo item.\n"
            raise PagePartNotFoundException()
        return divDOMs



class FFPage(PaginatedPage):

    def __init__(self, text):
        PaginatedPage.__init__(self, text)

    def oneFFListPart(self):
        """
        抽取列表的部分
        @raise PagePartNotFoundException: 当没有找到列表信息的页面部分时，抛出此异常
        """

        tag = "table"
        attr = ""
        value = ""
        ffTablesList = self.soup.findAll(tag)

        if ffTablesList is None:
            raise PagePartNotFoundException()

        return ffTablesList


class FollowPage(FFPage):

    def __init__(self, text):
        FFPage.__init__(self, text)

class FanPage(FFPage):

    def __init__(self, text):
        FFPage.__init__(self, text)


class UserInfoPage(Page):
    """
    """
    def __init__(self, text):
        Page.__init__(self, text)



