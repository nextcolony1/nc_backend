from steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.post import Post
import json
import time
import datetime
from datetime import timedelta, datetime
import requests
import pymysql.cursors


parameteraccount = "nextcolony"

def get_transactions():
    id = ""
    bid =""
    parameteraccount = "nextcolony"
    account = Account(parameteraccount)
    #this function is used to load transcations into a database
    account_history = list(account.get_account_history(-1, 10000, filter_by=["transfer"]))
    for transaction in account_history:
        try:
            memo = transaction["memo"]
            trx_id = transaction['trx_id']
            timestamp =transaction['timestamp']
            fromaccount = transaction["from"]
            if memo.startswith('nc'):
                #print (transaction)
                code, parameters = transaction["memo"].split("@")
                JSON = json.loads(parameters)
                #print(JSON)
                command = (JSON['command'])
                type = (JSON['type'])
                #print (type)
                #print (command)
                if type =="auctionbid":
                    bid = command['bid']
                    id = command['id']
                    #print (id)
                    #print (bid)
                    #print (transaction)

                    #write the transaction in the database
                    # Connect to the database

                    connection = pymysql.connect(host='localhost',
                                                 user='root',
                                                 password='PASSWORD',
                                                 db='steembattle',
                                                 charset='utf8mb4',
                                                 cursorclass=pymysql.cursors.DictCursor)
                    with connection.cursor() as cursor:
                        sql = ("SELECT * FROM `auction` WHERE `steem_trx` = '"+str(trx_id)+"'")
                        #print(sql)
                        cursor.execute(sql)
                        results = cursor.fetchone()
                        #print(results)
                        if results == None:
                           print ("Noch nicht vorhanden")
                           with connection.cursor() as cursor:
                               sql = ("INSERT INTO `auction` (`trx_id`, `steem_trx`, `timestamp`, `bid`, `planet_id`, `user`) VALUES (NULL, '"+str(trx_id)+"', '"+str(timestamp)+"', '"+str(bid)+"', '"+str(id)+"', '"+str(fromaccount)+"')")
                               print(sql)
                               cursor.execute(sql)
                               connection.commit()
                               connection.close()

                #print(JSON)

        except:
            continue

    return

if __name__ == '__main__':
    while True:
        try:
            get_transactions()
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasse$
            print ("Fehler")
