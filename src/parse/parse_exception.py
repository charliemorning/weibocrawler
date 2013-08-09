'''
#=============================================================================
#     FileName: parse_page.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:53
#      History:
#=============================================================================
'''
# -*- coding: UTF-8 -*-

import wexcept

class PagePartNotFoundException(wexcept.WeiboException):

	def __init__(self, msg='Part not found!'):

		wexcept.WeiboException.__init__(self, msg)

class UserIDNotFound(wexcept.WeiboException):

	def __init__(self, msg='User ID not found!'):

		wexcept.WeiboException.__init__(self, msg)

class UserCountStatParseError(wexcept.WeiboException):

	def __init__(self, msg='User ID not found!'):

		wexcept.WeiboException.__init__(self, msg)