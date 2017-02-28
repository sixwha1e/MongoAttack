#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__: sixwhale
import codecs
import inspect
import os
import random
import re
import requests
import string
import sys
import time
from colorama import Back
from colorama import Fore
from colorama import init
from colorama import Style
init(autoreset=True)
from Lib.setting import BURP_REQUEST_REGEX
from Lib.setting import BURP_XML_HISTORY_REGEX
from Lib.setting import CRAWL_EXCLUDE_EXTENSIONS
from Lib.setting import CUSTOM_INJECTION_MARK_CHAR
from Lib.setting import HEADERS
from Lib.setting import PROBLEMATIC_CUSTOM_INJECTION_PATTERNS
from Lib.setting import TAG_NO
from Lib.setting import TAG_YES

from pymongo import MongoClient

def printErrMsg(message):
	print(Back.RED+str(message))

def printInfoMsg(message):
	print(Fore.GREEN+str(message))

def filterStringValue(value, charRegex, replacement=""):
	"""
	Returns string value consisting only of chars satisfying supplied
	regular expression (note: it has to be in form [...])

	>>> filterStringValue(u'wzydeadbeef0123#', r'[0-9a-f]')
	u'deadbeef0123'
	"""
	retVal = value
	if value:
		retVal = re.sub(charRegex.replace("[", "[^") if "[^" not in charRegex else charRegex.replace("[^", "["), replacement, value)
	return retVal



def openFile(filename, mode='r', encoding='utf-8', errors="replace", buffering=1):
	try:
		return codecs.open(filename, mode, encoding, errors, buffering)
	except:
		print(Fore.RED + '[Error] There has been a file openning error for filename \'%s\'. Please check permissions...' % filename )



def getPublicTypeMembers(type_, onlyValues=False):
	retVal = []
	for name, value in inspect.getmembers(type_):
		if not name.startswith('__'):
			if not onlyValues:
				retVal.append((name, value))
			else:
				retVal.append(value)
	return retVal



def isListLike(value):
	return isinstance(value, (list, tuple, set, BigArray))


def getUnicode(value, encoding=None, noneToNull=False):
    """
    Return the unicode representation of the supplied value:

    >>> getUnicode(u'test')
    u'test'
    >>> getUnicode('test')
    u'test'
    >>> getUnicode(1)
    u'1'
    """
    if noneToNull and value is None:
    	return NULL
    if isinstance(value, unicode):
    	return value
    elif isinstance(value, basestring):
    	while True:
    		try:
    			return unicode(value, encoding or (kb.get("pageEncoding") if kb.get("originalPage") else None) or UNICODE_ENCODING)
    		except UnicodeDecodeError, e:
    			try:
    				return unicode(value, UNICODE_ENCODING)
    			except:
    				value = value[:e.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:e.end]) + value[e.end:]
    elif isListLike(value):
    	value = list(getUnicode(_, encoding, noneToNull) for _ in value)
    	return value
    else:
    	try:
    		return unicode(value)
    	except UnicodeDecodeError:
    		return unicode(str(value), errors="ignore")



def extractRegexResult(regex, content, flags=0):
	"""
	Returns 'result' group value from a possible match with regex on a given content
	
	>>> extractRegexResult(r'a(?P<result>[^g]+)g', 'abcdefg')
	'bcdef'
	"""
	retVal = None
	if regex and content and "?P<result>" in regex:
		match = re.search(regex, content, flags)
		if match:
			retVal = match.group("result")
	return retVal



def checkFile(filename, raiseOnError=True):
	valid = True

	try:
		if not os.path.isfile(filename):
			valid = False
	except UnicodeError:
		valid = False
	if valid:
		try:
			with open(filename,'rb'):
				pass
		except:
			valid = False
	if not valid and raiseOnError:
		print(Fore.RED + '[Error]: Can\'t read file %s' % filename)
	return valid

