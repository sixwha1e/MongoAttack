#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__: sixwhale
import getopt
import sys
from colorama import Back
from colorama import Fore
from colorama import init
from colorama import Style
init(autoreset=True)
from Lib.common import printCover
from Lib.common import printErrMsg
from Lib.common import printUsage
from Lib.setting import MY_IP
from Lib.setting import MY_PORT
from Mode.attack import mgAttack
from Mode.inject import InjectOption
from Mode.scan import scanMongoIP


def mongoAttack(port):
    port = port
    optlist,args = getopt.getopt(
        sys.argv[2:],
        't:p:c:'
    )
    for o,a in optlist:
        if o == '-t':
            ip = a
        elif o == '-p':
            port = int(a)
        elif o == '-c':
            clone_info = [1,a]
    mgAttack(ip,port,MY_IP,MY_PORT,clone_info)

def urlInject():
    optlist,args = getopt.getopt(
        sys.argv[2:],
        'u:r:'
    )
    for o,a in optlist:
        if o == '-u':
            url = a
            reqFile = None
        elif o == '-r':
            url = None
            reqFile = a
    InjectOption(url, reqFile)

def scanIP(scanNum):
    scanNum = scanNum
    optlist, args = getopt.getopt(
        sys.argv[2:],
        'n:'
    )
    for o,a in optlist:
        if o == '-n':
            scanNum = int(a)
    scanMongoIP(scanNum)

if __name__ == '__main__':
    url = None
    ip = None
    port = 27017
    scanNum = 10

    #参数设置
    try:
        optlist, args = getopt.getopt(
            sys.argv[1:],
            'h',
            ['mongo=','inject=','scan','help']
        )
        for o,a in optlist:
            if o == '--mongo':
                printCover()
                mongoAttack(port)
            if o == '--inject':
                printCover()
                urlInject()
            if o == '--scan':
                printCover()
                scanIP(scanNum)
            if o == '-h' or o == '--help':
                printCover()
                printUsage()
                exit()
    except Exception, e:
        printErrMsg('[Error] %s. Please use \'-h\' or \'--help\'' % e)
    if len(sys.argv) < 2:
        printCover()
        printUsage()