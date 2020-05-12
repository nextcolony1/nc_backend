import json
from datetime import timedelta, datetime
from beem.block import Block, BlockHeader
from beem.amount import Amount
from beem.blockchain import Blockchain
from beem import Steem
from beem.nodelist import NodeList
import requests
import time
import requests
import hashlib
import ast
import string
import base36
import random
import websocket
import sys
from random import randint
from utils.ncutils import checkifuser, findfreeplanet, shipdata, connectdb, get_shipdata,get_planetdata,get_distance,create_planet, read_config
from utils.ncutils import find_starterplanet_coords, generateUid, uid_from_block, write_spacedb, get_ship_data, get_item_data, get_planet_data, update_transaction_status, update_transfer_status
from commands import move_ship, explorespace, transport_resources, get_resource_levels, build_ship, enhance
from commands import upgrade, activate, adduser, buy
from process_transaction import get_transfer, get_transaction
from fix_data import fix_data
# get the productivity data from the SQL DB
# Connect to the database


#(id,name,bonus,planet_type,user,cords_hor,cords_ver,qty_copper,qty_uranium,qty_coal,qty_ore,level_uranium,level_copper,level_coal,level_ore,level_ship,\
#    level_base,level_research,level_coaldepot,level_oredepot,level_uraniumdepot,level_copperdepot,level_shipyard,ore_busy,copper_busy,coal_busy,uranium_busy,\
#    research_busy,base_busy,shipyard_busy,oredepot_busy,copperdepot_busy,coaldepot_busy,uraniumdepot_busy,last_update) = get_planetdata(3)


#result = explorespace(24,-1,-2)
#print (result)

#create_planet(19,19)


if __name__ == '__main__':
    
    parameter = {}
    upgrade_costs = {}
    upgrade_keys = ["shipyard", "oredepot", "copperdepot", "coaldepot", "uraniumdepot", "explorership",
                    "transportship", "scout", "patrol", "cutter", "corvette", "frigate", "destroyer", "cruiser", "battlecruiser",
                    "carrier", "dreadnought","yamato", "yamato1", "yamato2", "yamato3","yamato4","yamato5","yamato6","yamato7","yamato8","yamato9","yamato10","yamato11","yamato12",
                      "yamato13","yamato14","yamato15","yamato16","yamato17","yamato18","yamato19","yamato20","oremine", "coppermine", "coalmine", "uraniummine", "base",
                    "researchcenter", "bunker", "shieldgenerator", "explorership1", "transportship1", "transportship2"]
    
    connection = connectdb()
    table = connection["upgradecosts"]
    for key in upgrade_keys:
        upgrade_costs[key] = {}
        for x in range (1,21):
            result = table.find_one(name=key, level=x)
            if result is not None:
                upgrade_costs[key][str(x)] = result
    parameter["upgrade_costs"] = upgrade_costs
    skill_costs = {}
    skill_keys = ["shipyard", "oredepot", "copperdepot", "coaldepot", "uraniumdepot", "Explorer",
                    "Transporter", "Scout", "Patrol", "Cutter", "Corvette", "Frigate", "Destroyer", "Cruiser", "Battlecruiser",
                    "Carrier", "Dreadnought", "Yamato", "oremine", "coppermine", "coalmine", "uraniummine", "base", "researchcenter",
                    "orebooster", "coalbooster", "copperbooster", "uraniumbooster", "missioncontrol", "bunker",
                    "enlargebunker", "structureimprove", "armorimprove", "shieldimprove",
                    "rocketimprove", "bulletimprove", "laserimprove", "regenerationbonus", "repairbonus",
                    "shieldgenerator", "siegeprolongation", "depotincrease"]
    
    connection = connectdb()
    table = connection["skillcosts"]
    for key in skill_keys:
        skill_costs[key] = {}
        for x in range (1,21):
            result = table.find_one(name=key, level=x)
            if result is not None:
                skill_costs[key][str(x)] = result
    
    parameter["skill_costs"] = skill_costs
    
    
    
            # Read a single record
    production_rates = {}
    prodcution_keys = ["coalmine", "oremine", "coppermine", "uraniummine", "coaldepot", "oredepot", "copperdepot", "uraniumdepot"]
    
    connection = connectdb()
    table = connection["productivity"]
    for key in prodcution_keys:
        production_rates[key] = {}
        for x in range (0,21):
            result = table.find_one(name=key, level=x)
            if result is not None:
                production_rates[key][str(x)] = result
                
    parameter["production_rates"] = production_rates
    
    planet_rarity = {}
    connection = connectdb()
    table = connection["planetlevels"]
    for data in table.find():
        planet_rarity[data["rarity"]] = data
    
    parameter["planet_rarity"] = planet_rarity
    
    shipstats = {}
    
    connection = connectdb()
    table = connection["shipstats"]
    for result in table.find():
        if result is not None:
            shipstats[result["name"]] = result
                
    parameter["shipstats"] = shipstats    
    
    connection.executable.close()
    
    last_transaction_id = 0
    date = None
    earliest_trigger_date = None
    
    nodes = NodeList()
    node_update_count = 0
    nodes.update_nodes()
    stm = Steem(node=nodes.get_nodes(exclude_limited=False))
    print(nodes.get_nodes(exclude_limited=False))
    b = Blockchain(mode="head", max_block_wait_repetition=27, steem_instance=stm)  
    print("Start streaming - %s" % str(stm))
    last_vops_block_num = None
    last_vops_timestamp = None    
    last_vops_count_check = None
    while True:
        #try:
        if True:
            node_update_count += 1
            connection = connectdb()
            if node_update_count > 5000:
                
                nodes.update_nodes()
                node_update_count = 0
                stm = Steem(node=nodes.get_nodes(exclude_limited=False))   
                print("update node list: %s" % str(stm))
                b = Blockchain(mode="head", max_block_wait_repetition=27, steem_instance=stm)                   

            virtual_ops_found = False
            earlier_ops_found = False               
            trx_list = []

            
            table = connection["blocks"]
            current_block = table.find_one(order_by='-block_num')
            if current_block is None or ('block_num' in current_block and current_block['block_num'] is None):
                latest_block_num = b.get_current_block_num() 
            else:
                latest_block_num = current_block["block_num"]           
            
        
            
            table = connection["transactions"]
            trx_entry = table.find_one(tr_status=0, order_by='date')
            
            if trx_entry is not None:
                table = connection['status']
                table.upsert({"id": 1, "last_steem_block_num": latest_block_num, "first_unprocessed_block_num": trx_entry["block_num"]}, ["id"])                 
            else:
                table = connection['status']
                table.upsert({"id": 1, "last_steem_block_num": latest_block_num}, ["id"])                   
            table = connection["transactions"]
            if trx_entry is None:
                # print("Zero transaction found")
                #block = b.get_current_block()
                #date = block['timestamp'].replace(tzinfo=None)
                table = connection["blocks"]
                current_block = table.find_one(order_by='-block_num')
                if current_block is None or ('timestamp' in current_block and current_block['timestamp'] is None):
                    current_block = b.get_current_block()
                    date = current_block['timestamp'].replace(tzinfo=None) 
                else:
                    date = current_block['timestamp'].replace(tzinfo=None)                 
                
                
                table = connection["virtualops"]
                if last_vops_count_check is not None and (date - last_vops_count_check).total_seconds() < 6 and date > datetime(2019, 8, 2, 13, 38, 0):
                    vops_count = 0
                else:
                    start_time = time.time()
                    vops_count = table.count(tr_status=0, trigger_date={'<=': date})
                    print("vops count took %.2f s" % (time.time() - start_time))
                    last_vops_count_check = date                
                # print("vops for %s : %d" % (str(date), vops_count))
                start_time = time.time()
                block_num_est_method = "beem"
                if vops_count > 0:

                    # print(stm)
                    table = connection["blocks"]
                    current_block = table.find_one(order_by='-block_num')
                    if current_block is None or ('timestamp' in current_block and current_block['timestamp'] is None):
                        current_block = b.get_current_block()
                        if date > current_block['timestamp'].replace(tzinfo=None):
                            date = current_block['timestamp'].replace(tzinfo=None) 
                    else:
                        if date > current_block['timestamp'].replace(tzinfo=None):
                            date = current_block['timestamp'].replace(tzinfo=None) 
                        
                   
                    table = connection["virtualops"]
                    connection.begin()    
                    for vop in table.find(tr_status=0, trigger_date={'<=': date}, order_by='date', _limit=vops_count):
                        # print("vops %s" % str(vop["trigger_date"]))
                        virtual_ops_found = True
                        #print(vops["trigger_date"])
                        table3 = connection["blocks"]
                        block_data = table3.find_one(timestamp={"between": [vop["trigger_date"] - timedelta(seconds=1.51), vop["trigger_date"] + timedelta(seconds=1.51)]}, order_by="timestamp")
                        # block_data = table3.find_one(timestamp={"<=": vop["trigger_date"]},  order_by="-timestamp")
                        if block_data is not None:
                            block_num = block_data["block_num"]
                            timestamp = block_data["timestamp"]
                            block_num_est_method = "db"
                        elif vop["trigger_date"] == datetime(2019, 6, 18, 5 ,8, 27):
                            block_num = 33898184
                            timestamp = vop["trigger_date"]  
                        elif vop["trigger_date"] == datetime(2019, 6, 18, 5 ,8, 42):
                            block_num = 33898189
                            timestamp = vop["trigger_date"]  
                        elif vop["trigger_date"] == datetime(2019, 7, 30, 20,24,51):
                            timestamp = vop["trigger_date"]  
                            block_num = 35124173
                                                
                        else:
                            block_num_est_method = "beem"
                            if last_vops_timestamp is not None and abs((vop["trigger_date"] - last_vops_timestamp).total_seconds()) < 6:
                                print("diff  to last vops %.2s" % (vop["trigger_date"] - last_vops_timestamp).total_seconds())
                            block_num = b.get_estimated_block_num(vop["trigger_date"])
                            
                            last_vops_block_num = block_num
                            last_vops_timestamp = vop["trigger_date"]
                            try:
                                block = BlockHeader(block_num, steem_instance=stm)
                                timestamp = block['timestamp'].replace(tzinfo=None)
                            except:
                                timestamp = vop["trigger_date"]                            
                        print("Vops estimate %s took %.2f s - %s" % (str(vop["trigger_date"]), time.time() - start_time, block_num_est_method))
                        


                        table2 = connection["transactions"]  
                        data = dict(trx=vop["parent_trx"], user=vop["user"], tr_type=vop["tr_type"], block_num=block_num, tr_var1=vop["tr_var1"],
                                    tr_var2=vop["tr_var2"], tr_var3=vop["tr_var3"], tr_var4=vop["tr_var4"], tr_var5=vop["tr_var5"],
                                    tr_var6=vop["tr_var6"], tr_var7=vop["tr_var7"], tr_var8=vop["tr_var8"], tr_status=0 ,date=vop["trigger_date"],
                                    virtualop=1)
                        table2.insert(data)     
                        table2 = connection["virtualops"] 
                        table2.update({"id":vop["id"], "trigger_block_num": block_num, "tr_status": 1,
                                       "block_num": block_num, "block_date": timestamp}, ["id"])    
                    connection.commit() 
                    print("Vops processing took %.2f s - %s" % (time.time() - start_time, block_num_est_method))

            table = connection["transactions"]
            current_block_num = 0
            apply_fix = False
            for trx_data in table.find(tr_status=0, order_by='date', _limit=10):
                current_block_num = trx_data["block_num"]
                if not apply_fix and current_block_num >= 32578950 and current_block_num < 32578960:
                    apply_fix = True
                    table = connection["transactions"]
                    print("Single trigger to fix ship that were not returned")
                    for trx in table.find(tr_type="moveship", tr_status=2):
                        print(trx)
                        trx["tr_status"] = 0
                        table = connection["ships"]
                        ship = table.find_one(id=trx["tr_var1"])
                        ship["mission_busy_until"] = ship["busy_until"]
                        ship["busy_until"] = ship["created"]
                        table.update(ship, ["id"])
                        table = connection["transactions"]
                        table.update(trx, ["id"])
                elif not apply_fix and ((current_block_num >= 32578911 and current_block_num < 32578921)):
                    apply_fix = True
                    table = connection["transactions"]
                    print("Single trigger to fix ship that were not returned")
                    for trx in table.find(tr_type="explore", tr_status=2):
                        print(trx)
                        trx["tr_status"] = 0
                        table = connection["ships"]
                        ship = table.find_one(id=trx["tr_var1"])
                        ship["mission_busy_until"] = ship["busy_until"]
                        ship["busy_until"] = ship["created"]
                        table.update(ship, ["id"])
                        table = connection["transactions"]
                        table.update(trx, ["id"])
                elif not apply_fix and ((current_block_num >= 32582807 and current_block_num < 32582817)):
                    apply_fix = True
                    table = connection["transactions"]
                    print("Single trigger to fix ship that were not returned")
                    for trx in table.find(tr_type="explore", tr_status=2):
                        print(trx)
                        if trx["date"] <= datetime(2019, 5, 3, 8 ,38, 0):
                            continue
                        trx["tr_status"] = 0
                        table = connection["ships"]
                        ship = table.find_one(id=trx["tr_var1"])
                        ship["mission_busy_until"] = ship["busy_until"]
                        ship["busy_until"] = ship["created"]
                        table.update(ship, ["id"])
                        table = connection["transactions"]
                        table.update(trx, ["id"])                        
                if virtual_ops_found:
                    continue
                date = trx_data["date"]
                table = connection["virtualops"]
                
                if last_vops_count_check is not None and (date - last_vops_count_check).total_seconds() < 6 and date > datetime(2019, 8, 2, 13, 38, 0):
                    vops_count = 0
                else:
                    start_time = time.time()
                    vops_count = table.count(tr_status=0, trigger_date={'<=': date})
                    print("vops count took %.2f s" % (time.time() - start_time))
                    last_vops_count_check = date
                if vops_count > 0:
                    print("vops for %s : %d" % (str(date), vops_count))
                    # print(stm)
                    
                    table = connection["blocks"]
                    current_block = table.find_one(order_by='-block_num')
                    if current_block is None or ('timestamp' in current_block and current_block['timestamp'] is None):
                        current_block = b.get_current_block()
                        if date > current_block['timestamp'].replace(tzinfo=None):
                            date = current_block['timestamp'].replace(tzinfo=None) 
                    else:
                        if date > current_block['timestamp'].replace(tzinfo=None):
                            date = current_block['timestamp'].replace(tzinfo=None)                     
                    
                    connection.begin()      
                    for vop in table.find(tr_status=0, trigger_date={'<=': date}, order_by='date', _limit=vops_count):
                        # print("vops %s" % str(vop["trigger_date"]))
                        block_num_est_method = "beem"
                        virtual_ops_found = True
                        start_time_block = time.time()
                        table3 = connection["blocks"]
                        block_data = table3.find_one(timestamp={"between": [vop["trigger_date"] - timedelta(seconds=1.51), vop["trigger_date"] + timedelta(seconds=1.51)]},  order_by="timestamp")
                        # block_data = table3.find_one(timestamp={"<=": vop["trigger_date"]},  order_by="-timestamp")
                        if block_data is not None:
                            block_num = block_data["block_num"]              
                            block_num_est_method = "db"
                            timestamp = block_data["timestamp"]
                        elif vop["trigger_date"] == datetime(2019, 6, 18, 5 ,8, 27):
                            block_num = 33898184
                            timestamp = vop["trigger_date"]   
                        elif vop["trigger_date"] == datetime(2019, 6, 18, 5 ,8, 42):
                            block_num = 33898189
                            timestamp = vop["trigger_date"]   
                        elif vop["trigger_date"] == datetime(2019, 7, 30, 20,24,51):
                            block_num = 35124173
                            timestamp = vop["trigger_date"]   

                        else:
                            if last_vops_timestamp is not None and abs((vop["trigger_date"] - last_vops_timestamp).total_seconds()) < 6:
                                print("diff  to last vops %.2s" % (vop["trigger_date"] - last_vops_timestamp).total_seconds())
                            
                            block_num = b.get_estimated_block_num(vop["trigger_date"])
                            
                            last_vops_block_num = block_num
                            last_vops_timestamp = vop["trigger_date"]
                            
                            try:
                                block = BlockHeader(block_num, steem_instance=stm)
                                timestamp = block['timestamp'].replace(tzinfo=None)
                            except:
                                # stm.rpc.next()
                                # block = Block(block_num, steem_instance=stm)
                                timestamp = vop["trigger_date"]                            
                        print("Vops estimate %s took %.2f s - %s" % (str(vop["trigger_date"]), time.time() - start_time_block, block_num_est_method))                         
                            
                        
                        table2 = connection["transactions"]  
                        data = dict(trx=vop["parent_trx"], user=vop["user"], tr_type=vop["tr_type"], block_num=block_num, tr_var1=vop["tr_var1"],
                                    tr_var2=vop["tr_var2"], tr_var3=vop["tr_var3"], tr_var4=vop["tr_var4"], tr_var5=vop["tr_var5"],
                                    tr_var6=vop["tr_var6"], tr_var7=vop["tr_var7"], tr_var8=vop["tr_var8"], tr_status=0 ,date=vop["trigger_date"],
                                    virtualop=1)
                        table2.insert(data)     
                        table2 = connection["virtualops"] 
                        table2.update({"id":vop["id"], "trigger_block_num": block_num, "tr_status": 1,
                                       "block_num": block_num, "block_date": timestamp}, ["id"])   
                    connection.commit()
                    print("vops processing took %.2f s" % (time.time() - start_time))
                trx_list.append(trx_data)
            
       
            
            table = connection["transfers"]
            transfer_date = None
            for trx in table.find(tr_status=0, order_by='date', _limit=20 ):
                transfer_date = trx["date"]
                if transfer_date < date:
                    trx_list.append(trx)
                
            

            
            if virtual_ops_found or earlier_ops_found:
                trx_list = []
                continue
            sorted_trx = sorted(trx_list, key=lambda trx: trx["date"])
            for trx in sorted_trx:
                date = trx["date"]
                if "memo" in trx:
                    get_transfer(trx)
                else:
                    get_transaction(trx, parameter)
                    
            trx_list = []
            
        if date is not None:
            fix_data(date, parameter)

        #except Exception as inst:
        #    print(type(inst))    # the exception instance
        #    print(inst.args)     # arguments stored in .args
        #    print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasse$
        #    print ("Fehler")
        #time.sleep(3) 



