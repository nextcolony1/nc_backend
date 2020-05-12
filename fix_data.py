import json
from datetime import timedelta, datetime
from beem.block import Block
from beem.amount import Amount
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
from utils.ncutils import checkifuser, findfreeplanet, shipdata, connectdb, get_shipdata,get_planetdata,get_distance,create_planet
from utils.ncutils import find_starterplanet_coords, generateUid, uid_from_block, write_spacedb, get_ship_data, get_item_data, get_planet_data, update_transaction_status, update_transfer_status
from utils.ncutils import get_custom_json_id, get_transfer_id, get_mission_data
from commands import move_ship, explorespace, transport_resources, offload_deploy, offload_return, get_resource_levels, build_ship, enhance
from commands import upgrade, activate, adduser, buy, explore, finish_building, finish_skill, gift_item, update_ranking, gift_planet, deploy_ships, rename_planet
from commands import update_shop, attack, battle_return, cancel, support, enable, charge, finish_charging, offload_deploy_mission, siege
from commands import break_siege, fly_home_mission, offload_return_mission, issue
# get the productivity data from the SQL DB
# Connect to the database

def fix_data(time_now, parameter, test_mode=False):
    # get all open transactions from the database
    # Connect to the database
    
    start_time = time.time()
    
    apply_fix1 = False
    apply_fix2 = False
    apply_fix3 = False
    apply_fix4 = False
    apply_fix5 = False
    apply_fix6 = False
    apply_fix7 = False
    apply_fix8 = False
    apply_fix9 = False
    
    connection = connectdb()
    table = connection["status"]
    status = table.find_one(id=1)
    last_data_fix_date = status["last_data_fix_date"]
    if last_data_fix_date is None:
        last_data_fix_date = datetime(2019, 1, 1, 0, 0, 0)
    if time_now > datetime(2019, 7, 17, 9, 30, 0) and last_data_fix_date < datetime(2019, 7, 17, 9, 30, 0):
        apply_fix1 = True
    elif time_now > datetime(2019, 7, 17, 20, 0, 0) and last_data_fix_date < datetime(2019, 7, 17, 20, 0, 0):
        apply_fix2 = True
    elif time_now > datetime(2019, 7, 22, 9, 0, 0) and last_data_fix_date < datetime(2019, 7, 22, 9, 0, 0):
        apply_fix3 = True
    elif time_now > datetime(2019, 7, 22, 9, 35, 0) and last_data_fix_date < datetime(2019, 7, 22, 9, 35, 0):
        apply_fix4 = True    
    elif time_now > datetime(2019, 8, 22, 14, 20, 0) and last_data_fix_date < datetime(2019, 8, 22, 14, 20, 0):
        apply_fix5 = True     
    elif time_now > datetime(2019, 9, 4, 7, 0, 0) and last_data_fix_date < datetime(2019, 9, 4, 7, 0, 0):
        apply_fix6 = True          
    elif time_now > datetime(2019, 10, 10, 7, 0, 0) and last_data_fix_date < datetime(2019, 10, 10, 7, 0, 0):
        apply_fix7 = True         
    elif time_now > datetime(2019, 11, 6, 20, 30, 0) and last_data_fix_date < datetime(2019, 11, 6, 20, 30, 0):
        apply_fix8 = True      
    elif time_now > datetime(2019, 11, 10, 14, 40, 0) and last_data_fix_date < datetime(2019, 11, 10, 14, 40, 0):
        apply_fix9 = True     

    if test_mode:
        #apply_fix1 = True
        #apply_fix2 = True
        #apply_fix3 = True
        #apply_fix4 = True
        #apply_fix6 = True
        #apply_fix7 = True
        #apply_fix8 = True
        apply_fix9 = True
    elif apply_fix1 or apply_fix2 or apply_fix3 or apply_fix4 or apply_fix5 or apply_fix6 or apply_fix7 or apply_fix8 or apply_fix9:
        table = connection["status"]
        table.update({"last_data_fix_date": time_now}, ["id"])      
        
    if apply_fix1:
        print("Apply fix1")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 1000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue              
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=ship["cords_hor"], cords_ver=ship["cords_ver"])
            if planet is None:
                continue
            if planet["user"] == ship["user"]:
                continue
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
    
    
            #if mission["busy_until_return"] is None:
            #    continue
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            print(mission["mission_type"])
            table = connection['ships']
            print({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"])})
            if not test_mode:
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"])},['id'])

    if apply_fix2:
        print("Apply fix1")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 1000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue              
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=mission["cords_hor"], cords_ver=mission["cords_ver"])
            if planet is None:
                continue
            planet_id = planet["id"]
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
            table = connection["transactions"]
            vops = table.find_one(tr_var1=mission_id, tr_status=2)
            if vops is None:
                continue            
    
            #if mission["busy_until_return"] is None:
            #    continue
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            
            print(mission["mission_type"])
            table = connection['ships']
            print({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"])})
            if not test_mode:
                
                
                # check if there is enough resources on the starting planet - if not return False
                (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
                
                fin_qty_coal = float(new_qty_coal) + ship["qyt_coal"]
                fin_qty_ore = float(new_qty_ore) + ship["qyt_ore"]
                fin_qty_copper = float(new_qty_copper) + ship["qyt_copper"]
                fin_qty_uranium = float(new_qty_uranium) + ship["qyt_uranium"]
                
                    
                table = connection['ships']
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]),
                              "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                              "qyt_uranium": 0},['id'])
                    
                table = connection['planets']
                data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
                table.update(data,['id'])                    
                

    if apply_fix3:
        print("apply_fix3")
        if not test_mode:
            table = connection["stardust"]
            table.delete()
        
        table = connection["users"]
        update_amount = []
        for row in table.find():
            stardust_trx = []
            old_stardust = row["stardust"]
            amount = 0
            if row["date"] < datetime(2019, 7, 22, 10, 0, 0):
                table = connection["transactions"]
                new_user_trx = table.find_one(user=row["username"], tr_type="newuser", tr_status=1)
                if new_user_trx is not None:
                    
                    amount = int(10e8)
                    if not test_mode:
                        stardust_trx.append({"trx": new_user_trx["trx"], "tr_type": "gift", "tr_status": 1, "date": new_user_trx["date"],
                      "from_user":"nextcolony", "to_user":row["username"], "amount":int(10e8)})            
            
            table = connection["transfers"]
            for transfer in table.find(user=row["username"], tr_status=1):
                steem_amount = Amount(transfer["amount"])
                transfer_amount = int(float(steem_amount) * 100 * 1e8)
                if transfer["trx"] in ["1ac6dcbb7f4f4fc3864c570d909bc0081e80c997",
                                       "581c991f617393ebe87f305f724500edbc2b0181", "3d4dff0f428952dbc8b92d251bb029b2bb24774a",
                                       "e7f108ceb69df1d502f502325c53f1bb8b4a308d", "1c79290c4697ecb9aeffd9ab0a22091cba7c780f",
                                       "85950718febcb51ccdaad75dedcf4c0219d8ae95", "9c0afd10af78d414766a85b54f4ea27042b0f6c0",
                                       "8d8d8925fb80839c53c1023d1927fbfaac78a335"]:
                    continue
                amount += transfer_amount
                if not test_mode:
                    stardust_trx.append({"trx": transfer["trx"], "tr_type": "shop", "tr_status": 1, "date": transfer["date"], "to_user":transfer["user"], "amount":transfer_amount})
            table = connection["transactions"]
            for trx in table.find(user=row["username"], tr_type="transferstardust", tr_status=1):
                transfer_amount = int(float(trx["tr_var1"]) * 1e8)
                amount -= transfer_amount
                if not test_mode:
                    stardust_trx.append({"trx": trx["trx"], "tr_type": "transfer", "tr_status": 1, "date": trx["date"],
                  "from_user":trx["user"], "to_user":trx["tr_var2"], "amount":transfer_amount})
                
            for trx in table.find(tr_var2=row["username"], tr_type="transferstardust", tr_status=1):
                transfer_amount = int(float(trx["tr_var1"]) * 1e8)
                amount += transfer_amount
               
            if amount > 0:
                update_amount.append({"id": row["id"], "stardust": amount})
            if old_stardust is not None:
                print("%s %d -> %d" % (row["username"], old_stardust, amount))
            if len(stardust_trx) > 0 and not test_mode:
                table = connection["stardust"]
                connection.begin()
                for data in stardust_trx:
                    table.insert(data)
                connection.commit()
                stardust_trx = []
        
        if not test_mode:
            table = connection["users"]
            connection.begin()
            for user in update_amount:
                table.update(user, ["id"])
            connection.commit()  
            
            
    if apply_fix4:
        print("apply_fix4")

        
        auctions = [{"username": "sternenkrieger", "amount": 1379, "date": datetime(2019,3,25,8,39,0)},
                    {"username": "govinda71", "amount": 1350, "date": datetime(2019,3,26,17,56,0)},
                    {"username": "reggaemuffin", "amount": 1337, "date": datetime(2019,3,26,18,14,0)},
                    {"username": "mancer-sm-alt", "amount": 1500, "date": datetime(2019,4,7,22,20,0)},
                    {"username": "uraniumfuture", "amount": 1410, "date": datetime(2019,4,7,23,37,0)},
                    {"username": "urachem", "amount": 1503, "date": datetime(2019,4,8,8,42,0)},
                    {"username": "xx0xx", "amount": 30015, "date": datetime(2019,4,21,22,27,0)}]
        
        table = connection["users"]
        update_amount = []
        stardust_trx = []
        for user in auctions:
            user_data = table.find_one(username=user["username"])
            amount = user_data["stardust"] + int(user["amount"] * 100 * 1e8)
            stardust_data = table.find_one(to_user=user["username"], tr_type="auction")
            if stardust_data is None:
                    
                update_amount.append({"id": user_data["id"], "stardust": amount})
                
                stardust_trx.append({"tr_type": "auction", "tr_status": 1, "date": user["date"], "from_user": "nextcolony", "to_user":user["username"], "amount":int(user["amount"] * 100 * 1e8)})
    

        
        if not test_mode:
            table = connection["stardust"]
            connection.begin()
            for data in stardust_trx:
                table.insert(data)
            stardust_trx = []            
            table = connection["users"]
            for user in update_amount:
                table.update(user, ["id"])
            connection.commit()              
            
            
    if apply_fix5:
        print("apply_fix5")
        table = connection["shop"]
        booster_list = ["booster_01", "booster_02", "booster_03"]
        for b in booster_list:
            booster = table.find_one(itemid=b)
            table.update({"itemid": b, "boost_percentage": booster["boost_percentage"] * 2}, ["itemid"])
        table = connection["planets"]
        for planet in table.find(boost_percentage={">": 0}):
            if planet["boost_percentage"] == 0:
                continue
            table.update({"id": planet["id"], "boost_percentage": planet["boost_percentage"] * 2}, ["id"])

    if apply_fix6:
        print("Apply fix6")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        ship_cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 10000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue
            if ship["qyt_uranium"] == 0:
                continue
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=mission["cords_hor"], cords_ver=mission["cords_ver"])
            if planet is None:
                continue
            planet_id = planet["id"]
            
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
            table = connection["transactions"]
            vops = table.find_one(tr_var1=mission_id, tr_status=2)
            if vops is not None:
                continue
            #vops = table.find_one(tr_var1=mission_id, tr_status=1)
            #if vops is not None:
            #    print(vops)        
    
            #if mission["busy_until_return"] is None:
            #    continue
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            
            print(mission["mission_type"])
            table = connection['ships']
            ship_cnt += 1
            print({"cnt": ship_cnt, "id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]), "planet_id": planet_id, "user": mission["user"]})
            if not test_mode:
                # check if there is enough resources on the starting planet - if not return False
                (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
                
                fin_qty_coal = float(new_qty_coal) + ship["qyt_coal"]
                fin_qty_ore = float(new_qty_ore) + ship["qyt_ore"]
                fin_qty_copper = float(new_qty_copper) + ship["qyt_copper"]
                fin_qty_uranium = float(new_qty_uranium) + ship["qyt_uranium"]
                
                    
                table = connection['ships']
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]),
                              "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                              "qyt_uranium": 0},['id'])
                    
                table = connection['planets']
                data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
                table.update(data,['id'])   

    if apply_fix7:
        print("Apply fix7")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        ship_cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 10000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue
            if ship["qyt_uranium"] == 0:
                continue
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=mission["cords_hor"], cords_ver=mission["cords_ver"])
            if planet is None:
                continue
            planet_id = planet["id"]
            
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            
            print(mission["mission_type"])
            table = connection['ships']
            ship_cnt += 1
            print({"cnt": ship_cnt, "id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]), "planet_id": planet_id, "user": mission["user"]})
            if not test_mode:
                # check if there is enough resources on the starting planet - if not return False
                (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
                
                fin_qty_coal = float(new_qty_coal) + ship["qyt_coal"]
                fin_qty_ore = float(new_qty_ore) + ship["qyt_ore"]
                fin_qty_copper = float(new_qty_copper) + ship["qyt_copper"]
                fin_qty_uranium = float(new_qty_uranium) + ship["qyt_uranium"]
                
                    
                table = connection['ships']
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]),
                              "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                              "qyt_uranium": 0},['id'])
                    
                table = connection['planets']
                data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
                table.update(data,['id'])                   

    if apply_fix8:
        print("Apply fix8")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        ship_cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 10000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue
            if ship["qyt_uranium"] == 0:
                continue
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=mission["cords_hor"], cords_ver=mission["cords_ver"])
            if planet is None:
                continue
            planet_id = planet["id"]
            
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            
            print(mission["mission_type"])
            table = connection['ships']
            ship_cnt += 1
            print({"cnt": ship_cnt, "id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]), "planet_id": planet_id, "user": mission["user"]})
            if not test_mode:
                # check if there is enough resources on the starting planet - if not return False
                (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
                
                fin_qty_coal = float(new_qty_coal) + ship["qyt_coal"]
                fin_qty_ore = float(new_qty_ore) + ship["qyt_ore"]
                fin_qty_copper = float(new_qty_copper) + ship["qyt_copper"]
                fin_qty_uranium = float(new_qty_uranium) + ship["qyt_uranium"]
                
                    
                table = connection['ships']
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]),
                              "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                              "qyt_uranium": 0},['id'])
                    
                table = connection['planets']
                data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
                table.update(data,['id'])    

    if apply_fix9:
        print("Apply fix9")

        table = connection["ships"]
        ships = []
        for ship in table.find(mission_id={'not': None}):
            ships.append(ship["id"])
        print("%d ships found" % len(ships))
        cnt = 0
        ship_cnt = 0
        for shipid in ships:
            cnt += 1
            if cnt % 10000 == 0:
                print("%d/%d ships processed" % (cnt, len(ships)))
            table = connection["ships"]
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["mission_busy_until"] > time_now:
                continue            
            mission_id = ship["mission_id"]
            table = connection["missions"]
            mission = table.find_one(mission_id=mission_id)
            if mission is None:
                continue
            if ship["user"] != mission["user"]:
                continue
            if ship["cords_hor"] != mission["cords_hor_dest"]:
                continue
            if ship["cords_ver"] != mission["cords_ver_dest"]:
                continue
            if ship["qyt_uranium"] == 0:
                continue
    
            table = connection["planets"]
            planet = table.find_one(cords_hor=mission["cords_hor"], cords_ver=mission["cords_ver"])
            if planet is None:
                continue
            planet_id = planet["id"]
            
            vops_waiting = False
            table = connection["virtualops"]
            for vops in table.find(mission_id=mission_id):
                if vops["tr_status"] == 0:
                    vops_waiting = True
            if vops_waiting:
                continue
    
            if mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
                continue
            if mission["mission_type"] in ["support"]:
                continue
            
            print(mission["mission_type"])
            table = connection['ships']
            ship_cnt += 1
            print({"cnt": ship_cnt, "id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]), "planet_id": planet_id, "user": mission["user"]})
            if not test_mode:
                # check if there is enough resources on the starting planet - if not return False
                (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
                
                fin_qty_coal = float(new_qty_coal) + ship["qyt_coal"]
                fin_qty_ore = float(new_qty_ore) + ship["qyt_ore"]
                fin_qty_copper = float(new_qty_copper) + ship["qyt_copper"]
                fin_qty_uranium = float(new_qty_uranium) + ship["qyt_uranium"]
                
                    
                table = connection['ships']
                table.update({"id": str(shipid), "cords_hor": int(mission["cords_hor"]), "cords_ver": int(mission["cords_ver"]),
                              "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                              "qyt_uranium": 0},['id'])
                    
                table = connection['planets']
                data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
                table.update(data,['id'])       