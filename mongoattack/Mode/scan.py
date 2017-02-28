# -*- coding: utf-8 -*-
# __author__: sixwhale
import shodan
import socket
from Lib.common import printErrMsg
from Lib.setting import SHODAN_API_KEY
from pymongo import MongoClient


def scanMongoIP(scanNum):
    api = shodan.Shodan(SHODAN_API_KEY)
    print '[*] Start Scanning......'
    try:
        result = api.search('mongoDB')
        for index in range(scanNum):
            print '[*] Attacked IP: %s' % result['matches'][index]['ip_str']
    except shodan.APIError, e:
        printErrMsg('[Error] %s' % e)
