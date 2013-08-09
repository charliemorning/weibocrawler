# -*- coding: UTF-8 -*-
"""
#=============================================================================
#     FileName: net.py
#         Desc: 
#       Author: Charlie
#        Email: zhangchen143@gmail.com
#     HomePage: http://blog-charliemorning.rhcloud.com
#      Version: 0.0.1
#   LastChange: 2012-11-21 12:35:24
#      History:
#=============================================================================
"""

import cookielib
import time
import random


from config import *
from parse.extract import extractPwdName, extractVKValue, extractLoginRedirectionURL
from global_.util import get, post


def weibo_get(url, sleep=None, **kwargs):
	"""
	"""
	if len(kwargs) == 0:
		para = None
	else:
		para = kwargs

	if sleep is not None:
		time.sleep(sleep + random.randint(5, 10))
		 

	return get(url, para=para, cookie=Cookies.RequestCookie)

def weibo_post(url, **kwargs):
	"""
	"""
	if len(kwargs) == 0:
		para = None
	else:
		para = kwargs
	return post(url, para=para, cookie=Cookies.RequestCookie)

def requestLoginPageText():
	"""
	@raise WeiboRequestBaseError: 
	"""

	try:
		url = MobileLoginPageURL
		loginPage = get(url)
	except:
		err_msg = "failto request login page.\n" 
		raise

	return loginPage.read()


def makeLoginPostRequestData(name, password, pwdName, vk, **kwargs):
	"""
	"""
	
	data = {}
	
	mobile = name

	backURL = "http://weibo.com/"
	backTitle = "新浪微博"
		
	remember = "on"
	
	submit = "登录"
	
	data["mobile"] = mobile
	data[pwdName] = password
	data["remember"] = remember
	data['backURL'] = backURL
	data['backTitle'] = backTitle
	data['submit'] = submit
	data['vk'] = vk

	return data



def login(name, password):
	"""
	To login weibo
	@return: the main page of user and gsid
	
	@raise WeiboRequestBaseError: 当请求登陆页面失败时，抛出此异常;重定向到主页失败时抛出此异常
	@raise WeiboParsePatternError: 当无法解析密码时抛出此异常;解析VK值出错的时候，抛出此异常
	@raise PostRequestError: 当登陆失败是抛出此异常
	@raise WeiboTagSearchError: 当找不到重定向的URL时，抛出此异常
	@return: 用户登录后的主页面
	"""
	try:
	
		"Initiate cookie..."
	
		#初始化cookie文件
		Cookies.RequestCookie = cookielib.MozillaCookieJar(Cookies.CookieFile)
		Cookies.LoginCookie = cookielib.MozillaCookieJar(Cookies.LoginCookieFile)
		
		"Requesting login page..."
		
		#获取登陆页面    
		loginPage = get(MobileLoginPageURL)
		loginPageText = loginPage.read()
		
		"Exracting loging information..."
	
		#解析登陆密码中的随机码MobileLoginPageURL
		pwdName = extractPwdName(loginPageText)
		
		#解析vk
		vk = extractVKValue(loginPageText)
		
		#生成登陆需要的参数
		data = makeLoginPostRequestData(name, password, pwdName, vk)
		
		"Login..."
		
		#使用参数进行POST请求
		afterLogin = post(MobileLoginSubmitURL, data, Cookies.LoginCookie, receive=True)
		
		#登陆过后返回的页面
		text = afterLogin.read()
		
		print text
		
		"Redirect to main page..."
		
		#解析重定向链接
		redirectionURLAfterLogin = str(extractLoginRedirectionURL(text))
		
		print redirectionURLAfterLogin
	
		#请求主页面
		response = get(redirectionURLAfterLogin, para=None, cookie=Cookies.RequestCookie, receive=True)
	   
		mainPageText = response.read()
	
	except:
		raise

	return mainPageText