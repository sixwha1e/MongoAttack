# -*- coding: utf-8 -*-
# __author__: sixwhale
import shodan
import socket
from pymongo import MongoClient

from globalvalue import GlobalValue
def scanMongoIP(scanNum):
    api = shodan.Shodan(GlobalValue.shodan_api_key)
    print '[*] Start Scanning ......'
    try:
        result = api.search('mongoDB')
        for index in range(scanNum):
            print '[*] Attacked IP: %s' % result['matches'][index]['ip_str']
    except shodan.APIError, e:
        print '[x] Error: %s' % e
