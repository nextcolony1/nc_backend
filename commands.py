import json
from datetime import timedelta, datetime
from beem.block import Block, BlockHeader
from beem.amount import Amount
from beem.nodelist import NodeList

from beem import Steem
import requests
import time
import hashlib
import ast
import string
import base36
import math
import random
import websocket
import sys
import re
from random import randint
from utils.ncutils import checkifuser, findfreeplanet, shipdata, connectdb, get_shipdata,get_planetdata,get_distance,create_planet
from utils.ncutils import find_starterplanet_coords, uid_from_block, write_spacedb, get_ship_data, get_item_data, get_planet_data, update_transfer_status
from utils.ncutils import set_seed, uid_from_seed, get_is_empty_space, get_random_bonus, get_random_type, get_planetid, explore_planet, get_random_img
from utils.ncutils import get_flight_param, get_explorer_not_broke, get_free_solarsystem_in_donat, get_random_coords_in_solarsystem, coords_to_region, get_building_parameter
from utils.ncutils import coords_to_solarsystem, found_stardust, get_random_stardust, found_blueprint, get_random_blueprint, get_burn_income
from battle import apply_damage


def get_seed(block_num, trx_id):
    connection = connectdb()
    table = connection["blocks"]
    block = table.find_one(block_num=block_num)
    nodelist = NodeList()
    
    if block is None or (block is not None and (block["block_id"] is None or block["previous"] is None)):
        nodelist.update_nodes()
        stm = Steem(nodelist.get_nodes())
        try:
            block = Block(block_num, steem_instance=stm)
        except:
            block = Block(block_num, steem_instance=stm)
    seed = hashlib.md5((trx_id + block["block_id"] + block["previous"]).encode()).hexdigest() 
    return seed

def move_ship(shipid,cords_hor,cords_ver, mission_id, parameter, time_now):
    print("move_ship")
    shipstats = parameter["shipstats"]
    
    # Connect to the database
    connection = connectdb()
    table = connection["ships"]
    shipdata = table.find_one(id=shipid)

    if shipdata is None:
        print("Could not find id %s" % str(shipid))
        return False              
    cords_hor_cur = shipdata['cords_hor']
    cords_ver_cur = shipdata['cords_ver']
    qty_uranium = shipdata['qyt_uranium']

    distance = get_distance(cords_hor_cur,cords_ver_cur,int(cords_hor),int(cords_ver))
    if distance == 0:
        print("distance is zero, will not move.")
        return False
    type = shipdata['type']
    busy_until_old = shipdata['busy_until']
    mission_busy_until = shipdata['mission_busy_until']

    apply_battlespeed = False
    if shipdata["user"] is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=shipdata["user"])
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True
    
    print ("Distance to travel: "+str(distance))
    (uranium_consumption, flight_duration) = get_flight_param(shipstats[type],distance,apply_battlespeed)

    # calculate the time until arrival
    busy_until = time_now + timedelta(flight_duration / 24)
    print (mission_busy_until)
    #calculate the use of uranium
    print ("Uranium consumption: " +str(uranium_consumption))
    final_load_uranium = float(qty_uranium) - float(uranium_consumption)
    if final_load_uranium < 0:
        print("Not enough uranium to fly back. Use the invisible reserve tank.")
        final_load_uranium = 0
    # check if there is enough urannium on board
    table = connection["ships"]
    if (busy_until_old > time_now):
        print("Ship is still building")
        return (False)        
    elif (final_load_uranium >= 0) and (mission_busy_until <= time_now):
        print ("Enough uranium on board and the ship is not bsy. Ready for take off")
        #change the coordinates,the uranium level and the busy_until variables of the ship
        if time_now >= datetime(2019, 5, 3, 7, 40, 0):
            table.update({"id": shipid, "cords_hor": cords_hor, "cords_ver": cords_ver,
                          "mission_busy_until": busy_until, "qyt_uranium": final_load_uranium, "last_update": time_now}, ["id"])
        else:
            table.update({"id": shipid, "cords_hor": cords_hor, "cords_ver": cords_ver,
                          "mission_busy_until": mission_busy_until, "qyt_uranium": final_load_uranium, "last_update": time_now}, ["id"])            
    elif final_load_uranium >= 0 and (mission_busy_until > time_now):
        print ("Enough uranium on board, Ready for take off")
        #change the coordinates,the uranium level and the busy_until variables of the ship
        busy_until += (mission_busy_until - time_now)
        table.update({"id": shipid, "cords_hor": cords_hor, "cords_ver": cords_ver,
                      "mission_busy_until": busy_until, "qyt_uranium": final_load_uranium, "last_update": time_now}, ["id"])    
    else:
        print("Not enough uranium on board for the distance")
        return (False)
    return (True)

def explore(shipid, planet_id, mission_id, parameter, time_now, block_num, trx_id):
    (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,mission_id_tmp, home_planet_id) = get_shipdata(shipid)
    connection = connectdb()
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)
    c_hor = s_cords_hor
    c_ver = s_cords_ver
    
    uid_prefix = "P-"
    
    target_planet_id = get_planetid (c_hor,c_ver)
    table = connection['space']
    
    space_data = table.find_one(c_hor=int(c_hor), c_ver=int(c_ver))    
    if target_planet_id is not None or space_data is not None:
        table = connection["planets"]
        planet_data = table.find_one(id=planet_id)
        if planet_data is None:
            print("No planet there to return..")
            return False
        cords_hor = planet_data['cords_hor']
        cords_ver = planet_data['cords_ver']
        planetowner = planet_data['user']
        
        if time_now >= datetime(2019, 5, 3, 7, 40, 0):
            move_ship(shipid,cords_hor,cords_ver, mission_id, parameter, time_now)
        else:
            table = connection["virtualops"]    
            table.insert({"tr_status":0, "tr_type":"2", "tr_var1": shipid, "tr_var2": str(cords_hor), "tr_var3":str(cords_ver), "tr_var4": mission_id,
                          "date": time_now, "parent_trx": trx_id, "trigger_date": time_now, "user":planetowner})
                     
        table = connection["activity"]
        table.upsert({"user": s_user, "mission_id": mission_id, "type": "explore", "date": time_now,  "cords_hor": int(c_hor),
                        "cords_ver": int(c_ver), "result": "already_explored"}, ["mission_id"])     
        print ("This location is already explored! Flying back...")   
        return False      
    
    # random check if there is a planet
    find_prob = 0.01
    if s_type == "explorership1":
        table = connection["planets"]
        planet_data = table.find_one(id=planet_id)
        if planet_data is not None:
            cords_hor = planet_data['cords_hor']
            cords_ver = planet_data['cords_ver']
            planetowner = planet_data['user']
            distance = (get_distance(int(s_cords_hor),int(s_cords_ver),int(cords_hor),int(cords_ver)))
            find_prob =5.5e-2 * math.exp(-60 / distance)
            print("Explorer 2: distance %.2f droprate %.2f %%" % (distance, find_prob*100))
        
    
    if get_is_empty_space(find_prob):
        print ("no planet found")
        write_spacedb(c_hor,c_ver,s_user, time_now, block_num, trx_id)
        if get_explorer_not_broke():
                        
            # Stardust Found
            if found_stardust() and time_now >= datetime(2019, 10, 27, 13, 13, 13):
                if time_now >= datetime(2019, 11, 25, 19, 0, 0):
                    stardust_amount = get_random_stardust(10,200)
                else:
                    stardust_amount = get_random_stardust(10,300)
                print ("Stardust found: "+str(stardust_amount))
                
                int_amount = int(stardust_amount * 1e8)

                table = connection["users"]
                current_user = table.find_one(username = s_user)

                if current_user["stardust"] is not None:
                    current_stardust = int(current_user["stardust"])
                else: 
                    current_stardust = 0
                
                connection.begin()
                try:
                    new_stardust = current_stardust + int_amount
                    table.update({"username": s_user, "stardust": new_stardust }, ["username"]) 
                    table = connection["stardust"]
                    table.insert({"trx": trx_id ,"mission_id": mission_id, "tr_type": "exploration", "tr_status": 1, "date": time_now, "to_user":s_user, "amount":int_amount})
                    connection.commit()
                except:
                    connection.rollback()
                    print ("Database transaction failed")
                    return False

                # Blueprint found (and stardust)
                if found_blueprint():
                    itemid = get_random_blueprint()
                    print ("Blueprint found: "+ itemid)

                    table = connection["shop"]
                    shopitem = table.find_one(itemid=itemid)

                    seed = get_seed(block_num, trx_id)   
                    set_seed(seed)
                    connection.begin()
                    try:
                        uid = uid_from_seed(shopitem["prefix"])
                        table = connection["items"]
                        table.insert({"uid": uid, "owner": s_user, "date": time_now, "trx_id": trx_id, "block_num": block_num,
                                    "itemid": itemid})
                        connection.commit()
                    except:
                        connection.rollback() 
                        print ("Database transaction failed")
                        return False
                    table = connection["activity"]
                    table.upsert({"user": s_user, "mission_id": mission_id, "type": "explore", "date": time_now,  "cords_hor": int(c_hor),
                                "cords_ver": int(c_ver), "result": "blueprint_found", "new_item_id": itemid, "new_stardust": int_amount}, ["mission_id"])       
                else:
                    table = connection["activity"]
                    table.upsert({"user": s_user, "mission_id": mission_id, "type": "explore", "date": time_now,  "cords_hor": int(c_hor),
                                "cords_ver": int(c_ver), "result": "stardust_found", "new_stardust": int_amount}, ["mission_id"])   

            # Nothing Found
            else:
                print("Nothing found")
                table = connection["activity"]
                table.upsert({"user": s_user, "mission_id": mission_id, "type": "explore", "date": time_now,  "cords_hor": int(c_hor),
                            "cords_ver": int(c_ver), "result": "nothing_found"}, ["mission_id"]) 
            
            # Fly back explorer    
            table = connection["planets"]
            planet_data = table.find_one(id=planet_id)
            if planet_data is None:
                print("No planet there to return..")
                return False
            if planet_data is not None:
                cords_hor = planet_data['cords_hor']
                cords_ver = planet_data['cords_ver']
                planetowner = planet_data['user']                          
                if time_now >= datetime(2019, 5, 3, 7, 40, 0):
                    return move_ship(shipid,cords_hor,cords_ver, mission_id, parameter, time_now)
                else:
                    table = connection["virtualops"]    
                    table.insert({"tr_status":0, "tr_type":"moveship", "tr_var1": shipid, "tr_var2": str(cords_hor), "tr_var3":str(cords_ver),
                                "tr_var4": mission_id, "date": time_now, "parent_trx": trx_id, "trigger_date": time_now, "user":planetowner})                 

        else:
            # Explorer lost
            table = connection["ships"]
            table.delete(id=shipid)
            print("ship %s was destroyed during exploring .." % shipid)
          
            table = connection["activity"]
            table.upsert({"user": s_user, "mission_id": mission_id, "type": "explore", "date": time_now, "cords_hor": int(c_hor),
                          "cords_ver": int(c_ver), "result": "explorer_lost"}, ["mission_id"])  

            table = connection["missions"]
            table.update({"mission_id": mission_id,  "date": time_now, "busy_until_return": None}, ["mission_id"])            

    # Planet Found
    else:
        bonus = get_random_bonus()
        type = get_random_type()
        uid = uid_from_seed(uid_prefix)
        if time_now <= datetime(2019, 7, 1, 0, 0, 0):
            img_id = get_random_img(4)
        elif time_now <= datetime(2019, 11, 4, 21, 0, 0):
            img_id = get_random_img(5)
        elif time_now <= datetime(2019, 11, 15, 23, 0, 0):
            img_id = get_random_img(6) 
        elif time_now <= datetime(2019, 12, 12, 20, 0, 0):
            img_id = get_random_img(8)           
        else:
            img_id = get_random_img(9)
        if bonus == 4:
            table = connection["planets"]
            img_id = table.count(bonus=bonus, type=type, img_id={'<': 1000}) + 1
        print("planet %s was found!" % uid)
        table = connection["ships"]
        table.delete(id=shipid)
        
        # if there is a planet, generate the planet and explore the planet
        create_planet(c_hor,c_ver, uid, time_now, block_num, trx_id)
        explore_planet(uid, s_user, type, bonus, img_id, time_now)
        update_resource_rate(uid, parameter, time_now)
        # delete the explorer ship from the database
        table = connection["activity"]
        table.upsert({"user": s_user,  "mission_id": mission_id, "type": "explore", "date": time_now, "cords_hor": int(c_hor),
                    "cords_ver": int(c_ver), "result": "planet_found", "new_planet_id": uid}, ["mission_id"]) 
        table = connection["missions"]
        table.update({"mission_id": mission_id, "busy_until_return": None}, ["mission_id"])
        # Enter the cords into the space DB
        write_spacedb(c_hor,c_ver,s_user, time_now, block_num, trx_id, uid)

    return (True)

def explorespace(planet_id,c_hor,c_ver, ship_name, parameter, time_now, block_num, trx_id):
    print("explorespace")
    shipstats = parameter["shipstats"]
    if ship_name is not None and ship_name not in ["explorership", "explorership1"]:
        print("%s is not able to explore" % ship_name)
        return False
    elif ship_name is None:
        ship_name = "explorership"

    print(ship_name)
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)

    connection = connectdb()
    table = connection["planets"]
    planet_data = table.find_one(id=planet_id)
    
    if planet_data is None:
        print("No planet were found")
        return False    
    planetowner = planet_data['user']
    s_cords_hor = planet_data["cords_hor"]
    s_cords_ver = planet_data["cords_ver"]
    startplanet = planet_data["startplanet"]
    level_base = planet_data["level_base"]
    
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        print("wrong coordinates")
        return False

    if planet_data["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False
    
    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]   
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)


    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False   
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
        
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False
    
    table = connection["missions"]

    exploring_list = []
    for mission in table.find(mission_type="explorespace", cords_hor_dest=c_hor, cords_ver_dest=c_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] < time_now:
            continue
        exploring_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    if len(exploring_list) > 0 and time_now > datetime(2019, 7, 28, 9, 4, 0) and time_now < datetime(2019, 8, 22, 13, 45, 0):
        print("explorespace missions found: %s" % str(exploring_list))
        return False
    
    # Check for explorership
    table = connection["ships"]
    shipid = None
    for ship in table.find(type=ship_name, user=planetowner, cords_hor=s_cords_hor, cords_ver=s_cords_ver):
        if (ship["busy_until"] <= time_now) and shipid is None and (ship["mission_busy_until"] <= time_now) and ship["for_sale"] == 0:
            shipid = ship["id"]     
    if shipid is None:
        print("No free explorer %s was found." % ship_name)
        return False
    (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,mission_id, home_planet_id) = get_shipdata(shipid)
    
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    # check if there is a planet on the location already
    target_planet_id = get_planetid (c_hor,c_ver)
    if target_planet_id is not None:
        print ("There is already a planet on this location")
        return (False)
    
    table = connection['space']
    space_data = table.find_one(c_hor=int(c_hor), c_ver=int(c_ver))
    if space_data is not None:
        print ("This location is already explored!")
        return (False)    
    # calculate the distance to the target - and back
    print(c_hor)
    distance = (get_distance(int(s_cords_hor),int(s_cords_ver),int(c_hor),int(c_ver)))
    print (distance)

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True              
    (consumption, flight_duration) = get_flight_param(shipstats[s_type],distance,apply_battlespeed)
    
    print (consumption)
    # check if there is enough uranium available
    if (float(s_qty_uranium) + float(new_qty_uranium)) < float(consumption) * 2:
        print ("Not enough uranium") 
        print (new_qty_uranium)
        return (False)
        
    mission_id = uid_from_seed("M-")
    
    # calculate the time until arrival
    busy_until = time_now + timedelta(flight_duration / 24)
   
    # calculate how much uranium the ship has to load
    uranium_to_load = float(consumption) * 2 - float(s_qty_uranium)  
    
    final_p_qty_ore = float(new_qty_ore)
    final_p_qty_coal = float(new_qty_coal) 
    final_p_qty_copper = float(new_qty_copper) 
    final_p_qty_uranium = float(new_qty_uranium) - uranium_to_load  
    
    connection.begin()
    try:
        table = connection["planets"]
        table.update({"qyt_coal": final_p_qty_coal, "qyt_ore": final_p_qty_ore, "qyt_copper": final_p_qty_copper,
                    "qyt_uranium": final_p_qty_uranium, "last_update": str(time_now), "id": planet_id}, ["id"])  
        table = connection["ships"]
        if time_now <= datetime(2019, 5, 2, 20, 10, 00) or time_now >= datetime(2019, 5, 3, 7, 40, 0):
            table.update({"id": shipid, "cords_hor": int(c_hor), "cords_ver": int(c_ver),
                        "mission_busy_until": busy_until, "qyt_uranium": float(s_qty_uranium) + uranium_to_load, "last_update": time_now,
                        "mission_id": mission_id}, ["id"])
        else:
            table.update({"id": shipid, "cords_hor": int(c_hor), "cords_ver": int(c_ver),
                        "busy_until": busy_until, "mission_busy_until":  time_now + timedelta(flight_duration / 24) * 2, "qyt_uranium": float(s_qty_uranium) + uranium_to_load, "last_update": time_now,
                        "mission_id": mission_id}, ["id"])        
        
        table = connection["virtualops"]    
        table.insert({"tr_status":0, "tr_type":"explore", "tr_var1": shipid, "tr_var2": planet_id, "tr_var3": mission_id,
                    "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until, "user":planetowner, "mission_id": mission_id})
        table = connection["missions"]
        ships = {ship_name: 1}
        table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "explorespace",  "date": time_now, "busy_until": busy_until,
                    "cords_hor": s_cords_hor, "ships": json.dumps(ships),
                    "cords_ver": s_cords_ver, "cords_hor_dest": int(c_hor), "cords_ver_dest": int(c_ver), "busy_until_return": time_now + timedelta(flight_duration / 24) * 2})
        connection.commit()
    except:
        connection.rollback() 
        print ("Database transaction failed")
        return False        

    return (True)

# Command "transport"
def transport_resources(ship_list, planet_id, c_hor,c_ver ,qty_coal,qty_ore,qty_copper,qty_uranium, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    print("transport")
    connection = connectdb()
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        print("wrong coordinates")
        return False    

    if planet_from_data["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False

    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]   
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False         
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))   
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False
    
    if not isinstance(ship_list, (dict)):
        try:
            ship_list = {"transportship": int(ship_list)}
        except:
            print("Wrong format")
            return False
    table = connection["ships"]
    shipid_list = []
    ship_count = 0
    for shiptype in ship_list:
        print(shiptype)
        single_ship_list = []
        if not isinstance(ship_list[shiptype], (int, float)):
            print("Wrong format. %s" % str(shipid_list))
            return False
            
        ship_count += int(ship_list[shiptype])
        for ship in table.find(type=shiptype, user=planetowner, cords_hor=planet_from_data["cords_hor"], cords_ver=planet_from_data["cords_ver"]):
            if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_list[shiptype]) and (ship["mission_busy_until"] <= time_now) and ship["for_sale"] == 0:
                shipid_list.append(ship["id"])
                single_ship_list.append(ship["id"])
    if len(shipid_list) < ship_count:
        print("Not enough ships were found. %s" % str(shipid_list))
        return False
    ship_list = shipid_list    
    
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    ships = {}

    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   

        if ship["type"] in ships:
            ships[ship["type"]] += 1
        else:
            ships[ship["type"]] = 1    
    
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
          
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    consumption_by_ship = {}

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    for ship in ship_data:
        capacity = shipstats[ship["type"]]["capacity"]
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance, apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_by_ship[ship["id"]] = consumption
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)
        # calculate the number of ship needed
        
    
    t_arrival = time_now + timedelta(max_duration / 24)
    # calculate the number of ship needed
    try:
        total_load = float(qty_ore)  + float(qty_coal) + float(qty_copper) + float(qty_uranium)
    except:
        print("parameter are not valid!")
        return False
    
    if total_load > free_capacity:
        print("%d ships are not able to transport %.2f resources" % (len(ship_data), total_load))
        return False
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    if time_now < datetime(2019, 7, 17, 7, 30, 0):
        uranium_needed = (uranium_consumption) + float(qty_uranium)
    else:
        uranium_needed = (2 * uranium_consumption) + float(qty_uranium)
        
    if (float(qty_ore) > float (new_qty_ore)) or (float(qty_coal) > float (new_qty_coal)) or (float(qty_copper) > float (new_qty_copper)) or (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    if (float(qty_ore) < 0) or (float(qty_coal) < 0) or (float(qty_copper) < 0) or (float(qty_uranium) < 0): 
        print ("Ressources must be positive")
        return (False)
    table = connection["ships"]
        
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) - float(qty_coal)
    fin_qty_ore = float(new_qty_ore) - float(qty_ore)
    fin_qty_copper = float(new_qty_copper) - float(qty_copper)
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet
    q_coal = float(qty_coal)
    q_ore = float(qty_ore)
    q_copper = float(qty_copper)
    q_uranium = float(qty_uranium)
    
    connection.begin()
    for ship in ship_data:
        shipid = ship["id"]
        capacity = shipstats[ship["type"]]["capacity"]
        table = connection['ships']
        s_cap = 0
        s_qyt_coal = 0
        s_qyt_ore = 0
        s_qyt_copper = 0
        s_qyt_uranium = 0        
        if s_cap < float(capacity) and q_coal > 0:
            s_qyt_coal = max(min(q_coal, float(capacity) - s_cap), 0)
            s_cap += s_qyt_coal
            q_coal -= s_qyt_coal
        if s_cap < float(capacity) and q_ore > 0:
            s_qyt_ore = max(min(q_ore, float(capacity) - s_cap), 0)
            s_cap += s_qyt_ore         
            q_ore -= s_qyt_ore
        if s_cap < float(capacity) and q_copper > 0:
            s_qyt_copper = max(min(q_copper, float(capacity) - s_cap), 0)
            s_cap += s_qyt_copper
            q_copper -= s_qyt_copper
        if s_cap < float(capacity) and q_uranium > 0:
            s_qyt_uranium = max(min(q_uranium, float(capacity) - s_cap), 0)
            s_cap += s_qyt_uranium   
            q_uranium -= s_qyt_uranium
            
        if max_duration == 0:
            q_coal = float(qty_coal)
            q_ore = float(qty_ore)
            q_copper = float(qty_copper)
            q_uranium = float(qty_uranium)

            s_qyt_coal = 0
            s_qyt_ore = 0
            s_qyt_copper = 0
            s_qyt_uranium = 0
            print("self deploy, skipping vops")
        
        if time_now >= datetime(2019, 7, 17, 7, 30, 0):
            s_qyt_uranium += consumption_by_ship[shipid]
        table = connection['ships']
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                      "qyt_coal": s_qyt_coal, "qyt_ore": s_qyt_ore, "qyt_copper": s_qyt_copper, "mission_id": mission_id,
                      "qyt_uranium": s_qyt_uranium, "mission_busy_until": t_arrival},['id'])        
    
    if max_duration > 0:
        table = connection["virtualops"]
        table.insert({"tr_status":0, "tr_type":"offload_return_mission", "tr_var1": mission_id, "tr_var2": to_planet_id,
                      "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planetowner, "mission_id": mission_id})        
    

    print("remaining res.: %.2f %.2f %.2f %.2f" % (q_coal, q_ore, q_copper, q_uranium))
    fin_qty_coal = fin_qty_coal + q_coal
    qty_coal = float(qty_coal) - q_coal
    fin_qty_ore = fin_qty_ore + q_ore
    qty_ore = float(qty_ore) - q_ore
    fin_qty_copper = fin_qty_copper + q_copper
    qty_copper = float(qty_copper) - q_copper
    fin_qty_uranium = fin_qty_uranium + q_uranium
    qty_uranium = float(qty_uranium) - q_uranium
    
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "transport",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return": None, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": float(qty_coal), "qyt_ore": float(qty_ore), "qyt_copper": float(qty_copper),
                  "qyt_uranium": float(qty_uranium)})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    connection.commit()

    return (True)


def break_siege(ship_list, c_hor,c_ver ,start_planet_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    print("break_siege")
    connection = connectdb()
    table = connection["planets"]
    p = table.find_one(id=start_planet_id)
    if p is None:
        print("Could not find planet")
        return False  

    if p["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False    

    planetowner = p["user"]
    print(planetowner)
    table = connection["ships"]
    shipid_list = []
    ship_count = 0
    pos_list = {}
    class_list = []
    if not isinstance(ship_list, dict):
        print("Wrong type, must be a dict")
        return False
    
    type_counter = 0
    for shiptype in ship_list:
        type_counter += 1
        if not isinstance(ship_list[shiptype], dict):
            print("Wrong type, ship must be a dict")
            return False            
        if "n" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if "pos" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if ship_list[shiptype]["pos"] in pos_list:
            print("Each position can be used only once")
            return False
        if not isinstance(ship_list[shiptype]["pos"], int):
            print("pos must be int")
            return False        
        if ship_list[shiptype]["pos"] > 8 or ship_list[shiptype]["pos"] < 1:
            print("Position must be between 1-8")
            return False            
        pos_list[shiptype] = ship_list[shiptype]["pos"]
        if shiptype not in shipstats:
            print("Wrong type %s" % shiptype)
            return False            
        class_list.append(shipstats[shiptype]["class"])
    
    if type_counter > 8:
        print("Only 8 different types are allowed!")
        return False        
    elif type_counter == 0:
        print("At least one type is needed!")
        return False     
    for shiptype in ship_list:
        ship_entry = ship_list[shiptype]
        print(shiptype)
        single_ship_list = []
        ship_count += ship_entry["n"]
        
        for ship in table.find(type=shiptype, user=planetowner, cords_hor=p["cords_hor"], cords_ver=p["cords_ver"]):
            if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_entry["n"]) and (ship["mission_busy_until"] <= time_now or ship["mission_busy_until"] is None) and ship["for_sale"] == 0:
                shipid_list.append(ship["id"])
                single_ship_list.append(ship["id"])
    if len(shipid_list) < ship_count:
        print("Not enough ships were found.")
        return False
    ship_list = shipid_list
    planet_id = None
    planet_hor = None
    planet_ver = None
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    ships = {}
    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False
        if ship["type"] in ships:
            ships[ship["type"]] += 1
        else:
            ships[ship["type"]] = 1
    if planet_hor is None:
        print("Could not find planet_id")
        return False        
    planet_id = get_planetid (planet_hor, planet_ver)
    if planet_id is None:
        print("Could not find planet_id")
        return False     
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except: 
        print("wrong coordinates")
        return False    
    for ship in ship_data:
        if ship["cords_hor"] != s_cords_hor:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        if ship["cords_ver"] != s_cords_ver:
            print("Ship %s is at a wrong location" % ship["id"])
            return False    
    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]   
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False   
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0 and (s_cords_hor != int(c_hor) or s_cords_ver != int(c_ver)):
        print("Siege missions found: %s" % str(siege_list))
        return False        
    
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
  
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    consumption_ship = {}
    for ship in ship_data:
        
        capacity = shipstats[ship["type"]]["capacity"]    
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance,apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)       
    
    t_arrival = time_now + timedelta(max_duration / 24)

    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    uranium_needed = 2* (uranium_consumption)
    if (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) 
    fin_qty_ore = float(new_qty_ore) 
    fin_qty_copper = float(new_qty_copper) 
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet

    connection.begin()
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "breaksiege",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return":  time_now + timedelta(max_duration / 24)*2, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0, "qyt_uranium": 0})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    
    for ship in ship_data:
        shipid = ship["id"]
        position = pos_list[ship["type"]]
        table = connection['ships']
        
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                       "mission_busy_until": t_arrival, "position": position, "qyt_uranium": consumption_ship[shipid],
                       "mission_id": mission_id},['id'])
    connection.commit()
    # write an "offload" transaction into the transactions db, with a time set to the arrival time of the ships
    print("write vops")
    table = connection["virtualops"]
    table.insert({"tr_status":0, "tr_type":"battle_return", "tr_var1": mission_id, "tr_var2": start_planet_id, "tr_var3": "siege",
                  "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planetowner, "mission_id": mission_id})
    
    return (True)         

# Command "attack"
def attack(ship_list, c_hor,c_ver ,start_planet_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    print("transport")
    connection = connectdb()
    table = connection["planets"]
    p = table.find_one(id=start_planet_id)
    if p is None:
        print("Could not find planet")
        return False    
    if p["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False        
    planetowner = p["user"]
    print(planetowner)
    table = connection["ships"]
    shipid_list = []
    ship_count = 0
    pos_list = {}
    class_list = []
    if not isinstance(ship_list, dict):
        print("Wrong type, must be a dict")
        return False
    
    type_counter = 0
    for shiptype in ship_list:
        type_counter += 1
        if not isinstance(ship_list[shiptype], dict):
            print("Wrong type, ship must be a dict")
            return False            
        if "n" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if "pos" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if ship_list[shiptype]["pos"] in pos_list:
            print("Each position can be used only once")
            return False
        if not isinstance(ship_list[shiptype]["pos"], int):
            print("pos must be int")
            return False        
        if ship_list[shiptype]["pos"] > 8 or ship_list[shiptype]["pos"] < 1:
            print("Position must be between 1-8")
            return False            
        pos_list[shiptype] = ship_list[shiptype]["pos"]
        if shiptype not in shipstats:
            print("Wrong type %s" % shiptype)
            return False            
        class_list.append(shipstats[shiptype]["class"])
    
    if type_counter > 8:
        print("Only 8 different types are allowed!")
        return False        
    elif type_counter == 0:
        print("At least one type is needed!")
        return False     
    for shiptype in ship_list:
        ship_entry = ship_list[shiptype]
        print(shiptype)
        single_ship_list = []
        ship_count += ship_entry["n"]
        
        for ship in table.find(type=shiptype, user=planetowner, cords_hor=p["cords_hor"], cords_ver=p["cords_ver"]):
            if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_entry["n"]) and (ship["mission_busy_until"] <= time_now or ship["mission_busy_until"] is None) and ship["for_sale"] == 0:
                shipid_list.append(ship["id"])
                single_ship_list.append(ship["id"])
    if len(shipid_list) < ship_count:
        print("Not enough ships were found.")
        return False
    ship_list = shipid_list
    planet_id = None
    planet_hor = None
    planet_ver = None
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    ships = {}
    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False
        if ship["type"] in ships:
            ships[ship["type"]] += 1
        else:
            ships[ship["type"]] = 1
    if planet_hor is None:
        print("Could not find planet_id")
        return False        
    planet_id = get_planetid (planet_hor, planet_ver)
    if planet_id is None:
        print("Could not find planet_id")
        return False     
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        
        print("wrong coordinates")
        return False    
    for ship in ship_data:
        if ship["cords_hor"] != s_cords_hor:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        if ship["cords_ver"] != s_cords_ver:
            print("Ship %s is at a wrong location" % ship["id"])
            return False    
    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]    
            

    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False   
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue   
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False        
    
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
  
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    consumption_ship = {}
    for ship in ship_data:
        
        # calculate the arrival time of the ships
        capacity = shipstats[ship["type"]]["capacity"]    
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance, apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)
        # calculate the number of ship needed
        
    t_arrival = time_now + timedelta(max_duration / 24)

    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    uranium_needed = 2* (uranium_consumption)
    if (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) 
    fin_qty_ore = float(new_qty_ore) 
    fin_qty_copper = float(new_qty_copper) 
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet

    connection.begin()
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "attack",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return":  time_now + timedelta(max_duration / 24)*2, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0, "qyt_uranium": 0})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    
    for ship in ship_data:
        shipid = ship["id"]
        position = pos_list[ship["type"]]
        table = connection['ships']
        
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                       "mission_busy_until": t_arrival, "position": position, "qyt_uranium": consumption_ship[shipid],
                       "mission_id": mission_id},['id'])
    connection.commit()
    # write an "offload" transaction into the transactions db, with a time set to the arrival time of the ships
    print("write vops")
    table = connection["virtualops"]
    table.insert({"tr_status":0, "tr_type":"battle_return", "tr_var1": mission_id, "tr_var2": start_planet_id,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planetowner, "mission_id": mission_id})
    
    return (True)         


def siege(ship_list, c_hor,c_ver ,start_planet_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    print("siege")
    connection = connectdb()
    table = connection["planets"]
    p = table.find_one(id=start_planet_id)
    if p is None:
        print("Could not find planet")
        return False
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        print("wrong coordinates")
        return False  
    if p["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False

    if p["cords_hor"] == int(c_hor) and p["cords_ver"] == int(c_ver):
        print("cannot siege myself")
        return False        
    planetowner = p["user"]
    print(planetowner)
    table = connection["ships"]
    shipid_list = []
    ship_count = 0
    pos_list = {}
    class_list = []
    if not isinstance(ship_list, dict):
        print("Wrong type, must be a dict")
        return False
    
    ship_array = []
    for shiptype in ship_list:
        if not isinstance(ship_list[shiptype], dict):
            print("Wrong type, ship must be a dict")
            return False            
        if "n" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if "pos" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if ship_list[shiptype]["pos"] in pos_list:
            print("Each position can be used only once")
            return False
        if not isinstance(ship_list[shiptype]["pos"], int):
            print("pos must be int")
            return False        
        if ship_list[shiptype]["pos"] > 8 or ship_list[shiptype]["pos"] < 1:
            print("Position must be between 1-8")
            return False            
        pos_list[shiptype] = ship_list[shiptype]["pos"]
        if shiptype not in shipstats:
            print("Wrong type %s" % shiptype)
            return False            
        ship_list[shiptype]["type"] = shiptype
        ship_array.append(ship_list[shiptype])
        class_list.append(shipstats[shiptype]["class"])
    
    sorted_ship_list = sorted(ship_array, key=lambda d: d["pos"])
    
    
    for shiptype in ship_list:
        ship_entry = ship_list[shiptype]
        print(ship_entry)
        print(time_now)
        single_ship_list = []
        ship_count += ship_entry["n"]
        
        for ship in table.find(type=shiptype, user=planetowner, cords_hor=p["cords_hor"], cords_ver=p["cords_ver"]):
            if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_entry["n"]) and (ship["mission_busy_until"] <= time_now or ship["mission_busy_until"] is None) and ship["for_sale"] == 0:
                shipid_list.append(ship["id"])
                single_ship_list.append(ship["id"])
            else:
                print(ship)
    if len(shipid_list) < ship_count:
        print("Not enough ships were found.")
        return False
    ships = {}
    for ship in sorted_ship_list:
        ships[ship["type"]] = ship["n"]
    
    ship_list = shipid_list
    planet_id = None
    planet_hor = None
    planet_ver = None
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    
    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False

    if planet_hor is None:
        print("Could not find planet_id")
        return False        
    planet_id = get_planetid (planet_hor, planet_ver)
    if planet_id is None:
        print("Could not find planet_id")
        return False     
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
  
    for ship in ship_data:
        if ship["cords_hor"] != s_cords_hor:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        if ship["cords_ver"] != s_cords_ver:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        

    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"]  
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]   
            
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False   
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False    

    siegeduration_h = 6
    if userdata is not None:
        if userdata["r_siegeprolongation"] is not None:
            siegeduration_h = (userdata["r_siegeprolongation"]) * 1.5 + 6 
    print("Siege duration is %.2f h" % siegeduration_h)

    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
  
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    consumption_ship = {}
    for ship in ship_data:
        capacity = shipstats[ship["type"]]["capacity"]    
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance, apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)
        # calculate the number of ship needed
        
    
    t_arrival = time_now + timedelta(max_duration / 24)

    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    uranium_needed = 2* (uranium_consumption)
    if (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) 
    fin_qty_ore = float(new_qty_ore) 
    fin_qty_copper = float(new_qty_copper) 
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet
    
    busy_until_return = t_arrival +  timedelta(siegeduration_h / 24)
    
    connection.begin()
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "siege",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return":  busy_until_return, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0, "qyt_uranium": 0})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    
    for ship in ship_data:
        shipid = ship["id"]
        position = pos_list[ship["type"]]
        table = connection['ships']
        
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                       "mission_busy_until": t_arrival, "position": position, "qyt_uranium": consumption_ship[shipid],
                       "mission_id": mission_id},['id'])
    # write an "offload" transaction into the transactions db, with a time set to the arrival time of the ships
    connection.commit()
    table = connection["virtualops"]
    table.insert({"tr_status":0, "tr_type":"fly_home_mission", "tr_var1": mission_id, "tr_var2": planet_id,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until_return, "user":planetowner, "mission_id": mission_id})        
    
    return (True)    


def support(ship_list, c_hor,c_ver ,start_planet_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    print("support")
    connection = connectdb()
    table = connection["planets"]
    p = table.find_one(id=start_planet_id)
    if p is None:
        print("Could not find planet")
        return False  
    if p["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False              
    planetowner = p["user"]
    print(planetowner)
    table = connection["ships"]
    shipid_list = []
    ship_count = 0
    pos_list = {}
    class_list = []
    if not isinstance(ship_list, dict):
        print("Wrong type, must be a dict")
        return False
    
    ship_array = []
    for shiptype in ship_list:
        if not isinstance(ship_list[shiptype], dict):
            print("Wrong type, ship must be a dict")
            return False            
        if "n" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if "pos" not in ship_list[shiptype]:
            print("Wrong input format")
            return False
        if ship_list[shiptype]["pos"] in pos_list:
            print("Each position can be used only once")
            return False
        if not isinstance(ship_list[shiptype]["pos"], int):
            print("pos must be int")
            return False
        if ship_list[shiptype]["pos"] > 8 or ship_list[shiptype]["pos"] < 1:
            print("Position must be between 1-8")
            return False            
        pos_list[shiptype] = ship_list[shiptype]["pos"]
        if shiptype not in shipstats:
            print("Wrong type %s" % shiptype)
            return False            

        ship_list[shiptype]["type"] = shiptype
        ship_array.append(ship_list[shiptype])
        class_list.append(shipstats[shiptype]["class"])
    
    sorted_ship_list = sorted(ship_array, key=lambda d: d["pos"])
    
    
    for shiptype in ship_list:
        ship_entry = ship_list[shiptype]
        print(ship_entry)
        print(time_now)
        single_ship_list = []
        ship_count += ship_entry["n"]
        
        for ship in table.find(type=shiptype, user=planetowner, cords_hor=p["cords_hor"], cords_ver=p["cords_ver"]):
            if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_entry["n"]) and (ship["mission_busy_until"] <= time_now or ship["mission_busy_until"] is None) and ship["for_sale"] == 0:
                shipid_list.append(ship["id"])
                single_ship_list.append(ship["id"])
            else:
                print(ship)
    if len(shipid_list) < ship_count:
        print("Not enough ships were found.")
        return False
    ships = {}
    for ship in sorted_ship_list:
        ships[ship["type"]] = ship["n"]
    
    ship_list = shipid_list
    planet_id = None
    planet_hor = None
    planet_ver = None
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    
    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False

    if planet_hor is None:
        print("Could not find planet_id")
        return False        
    planet_id = get_planetid (planet_hor, planet_ver)
    if planet_id is None:
        print("Could not find planet_id")
        return False     
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        
        print("wrong coordinates")
        return False    
    for ship in ship_data:
        if ship["cords_hor"] != s_cords_hor:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        if ship["cords_ver"] != s_cords_ver:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        

    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]                
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False   
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False       
    
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
  
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    consumption_ship = {}
    for ship in ship_data:
        capacity = shipstats[ship["type"]]["capacity"]    
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance,apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)
        # calculate the number of ship needed
        
    t_arrival = time_now + timedelta(max_duration / 24)

    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    uranium_needed = 2* (uranium_consumption)
    if (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) 
    fin_qty_ore = float(new_qty_ore) 
    fin_qty_copper = float(new_qty_copper) 
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet

    connection.begin()
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "support",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return":  None, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0, "qyt_uranium": 0})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    
    for ship in ship_data:
        shipid = ship["id"]
        position = pos_list[ship["type"]]
        table = connection['ships']
        
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                       "mission_busy_until": t_arrival, "position": position, "qyt_uranium": consumption_ship[shipid],
                       "mission_id": mission_id},['id'])
    connection.commit()
    return (True)         

# Command "deploy"
def deploy_ships(ship_list, c_hor,c_ver ,qty_coal,qty_ore,qty_copper,qty_uranium, start_planet_id, parameter, time_now, block_num, trx_id):

    print("deploy")
    shipstats = parameter["shipstats"]
    connection = connectdb()
    if start_planet_id is None:
        if isinstance(ship_list, str) and ship_list.find(",") > -1:
            ship_list = ship_list.split(",")
        elif isinstance(ship_list, str) and ship_list.find(";") > -1:
            ship_list = ship_list.split(";")        
        elif isinstance(ship_list, str):
            ship_list = [ship_list]
    else:
        table = connection["planets"]
        p = table.find_one(id=start_planet_id)
        if p is None:
            print("Could not find planet")
            return False            
        planetowner = p["user"]
        print(planetowner)
        table = connection["ships"]
        shipid_list = []
        ship_count = 0
        try:
            for shiptype in ship_list:
                print(shiptype)
                single_ship_list = []
                if not isinstance(ship_list[shiptype], (int, float)):
                    print("Wrong format. %s" % str(shipid_list))
                    return False
                
                ship_count += int(ship_list[shiptype])
                for ship in table.find(type=shiptype, user=planetowner, cords_hor=p["cords_hor"], cords_ver=p["cords_ver"]):
                    if (ship["busy_until"] <= time_now) and len(single_ship_list) < int(ship_list[shiptype]) and (ship["mission_busy_until"] <= time_now) and ship["for_sale"] == 0:
                        shipid_list.append(ship["id"])
                        single_ship_list.append(ship["id"])
            if len(shipid_list) < ship_count:
                print("Not enough ships were found. %s" % str(shipid_list))
                return False
        except:
            return False
        ship_list = shipid_list
    planet_id = None
    planet_hor = None
    planet_ver = None
    ship_data = []
    table = connection["ships"]
    print(ship_list)
    ships = {}

    for shipid in ship_list:
        ship = table.find_one(id=shipid)
        ship_data.append(ship)
        if ship is None:
            print("Could not find ship %s" % shipid)
            return False 
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % shipid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % shipid)
            return False   
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False
        if ship["type"] in ships:
            ships[ship["type"]] += 1
        else:
            ships[ship["type"]] = 1
    if planet_hor is None:
        print("Could not find planet_id")
        return False        
    planet_id = get_planetid (planet_hor, planet_ver)
    if planet_id is None:
        print("Could not find planet_id")
        return False     
    table = connection["planets"]
    planet_from_data = table.find_one(id=planet_id)
    if planet_from_data is None:
        print("Could not find planet_id")
        return False
    planetowner = planet_from_data['user']
    s_cords_hor = planet_from_data["cords_hor"]
    s_cords_ver = planet_from_data["cords_ver"]
    startplanet = planet_from_data["startplanet"]
    level_base = planet_from_data["level_base"]
    try:
        print("%s, %s" % (int(c_hor), int(c_ver)))
    except:
        print("wrong coordinates")
        return False   
    if planet_from_data["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False 
    for ship in ship_data:
        if ship["cords_hor"] != s_cords_hor:
            print("Ship %s is at a wrong location" % ship["id"])
            return False
        if ship["cords_ver"] != s_cords_ver:
            print("Ship %s is at a wrong location" % ship["id"])
            return False    
    to_planet_id = get_planetid (int(c_hor), int(c_ver))
    if to_planet_id is None:    
        print("No planet at %d/%d was found" % (int(c_hor), int(c_ver)))
        return False

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]    
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=s_cords_hor ,cords_ver=s_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False 
    if allowed_missions <= running_missions:
        print("%d/%d missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # check for siege
    table = connection["missions"]
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=s_cords_hor, cords_ver_dest=s_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False    
    
    
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)

    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
    planet_to_owner = planet_to_data['user']
  
    distance = get_distance(planet_from_data['cords_hor'],planet_from_data['cords_ver'],planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if planetowner is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=planetowner)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0
    for ship in ship_data:
        capacity = shipstats[ship["type"]]["capacity"]
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance,apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
            
        uranium_consumption += consumption
    
        # calculate the free capacity per ship
        free_capacity += float(capacity)
        # calculate the number of ship needed
        
    
    t_arrival = time_now + timedelta(max_duration / 24)
    try:
        total_load = float(qty_ore)  + float(qty_coal) + float(qty_copper) + float(qty_uranium)
    except:
        print("parameter are not valid!")
        return False
    
    if total_load > free_capacity:
        print("%d ships are not able to transport %.2f resources" % (len(ship_data), total_load))
        return False
    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    uranium_needed = (uranium_consumption) + float(qty_uranium)
    if (float(qty_ore) > float (new_qty_ore)) or (float(qty_coal) > float (new_qty_coal)) or (float(qty_copper) > float (new_qty_copper)) or (float(uranium_needed) > float (new_qty_uranium)): 
        print ("Not enough ressources")
        return (False)
    if (float(qty_ore) < 0) or (float(qty_coal) < 0) or (float(qty_copper) < 0) or (float(qty_uranium) < 0): 
        print ("Ressources must be positive")
        return (False)    
    
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) - float(qty_coal)
    fin_qty_ore = float(new_qty_ore) - float(qty_ore)
    fin_qty_copper = float(new_qty_copper) - float(qty_copper)
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_needed)
    print(fin_qty_coal)
    # reduce the ressource level on the starting planet
    
    q_coal = float(qty_coal)
    q_ore = float(qty_ore)
    q_copper = float(qty_copper)
    q_uranium = float(qty_uranium)
    
    connection.begin()
    for ship in ship_data:
        shipid = ship["id"]
        if time_now > datetime(2019, 5, 28, 8, 30, 0):
            capacity = shipstats[ship["type"]]["capacity"]
        # print("test2: %s" % shipid)
        table = connection['ships']
        s_cap = 0
        s_qyt_coal = 0
        s_qyt_ore = 0
        s_qyt_copper = 0
        s_qyt_uranium = 0        
        if s_cap < float(capacity) and q_coal > 0:
            s_qyt_coal = max(min(q_coal, float(capacity) - s_cap), 0)
            s_cap += s_qyt_coal
            q_coal -= s_qyt_coal
        if s_cap < float(capacity) and q_ore > 0:
            s_qyt_ore = max(min(q_ore, float(capacity) - s_cap), 0)
            s_cap += s_qyt_ore         
            q_ore -= s_qyt_ore
        if s_cap < float(capacity) and q_copper > 0:
            s_qyt_copper = max(min(q_copper, float(capacity) - s_cap), 0)
            s_cap += s_qyt_copper
            q_copper -= s_qyt_copper
        if s_cap < float(capacity) and q_uranium > 0:
            s_qyt_uranium = max(min(q_uranium, float(capacity) - s_cap), 0)
            s_cap += s_qyt_uranium   
            q_uranium -= s_qyt_uranium
            
        if time_now < datetime(2019, 6, 23, 13, 0, 0) or max_duration > 0:
            print("write vops")
        else:
            q_coal = float(qty_coal)
            q_ore = float(qty_ore)
            q_copper = float(qty_copper)
            q_uranium = float(qty_uranium)

            s_qyt_coal = 0
            s_qyt_ore = 0
            s_qyt_copper = 0
            s_qyt_uranium = 0
            print("self deploy, skipping vops")

        table = connection['ships']
        table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                      "qyt_coal": s_qyt_coal, "qyt_ore": s_qyt_ore, "qyt_copper": s_qyt_copper, "mission_id": mission_id,
                      "qyt_uranium": s_qyt_uranium, "mission_busy_until": t_arrival},['id'])        
    connection.commit()
    
    if time_now < datetime(2019, 6, 23, 13, 0, 0) or max_duration > 0:
        table = connection["virtualops"]
        table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": to_planet_id,
                      "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planetowner, "mission_id": mission_id})        
    

    print("remaining res.: %.2f %.2f %.2f %.2f" % (q_coal, q_ore, q_copper, q_uranium))
    if time_now > datetime(2019, 5, 28, 8, 30, 0):
        fin_qty_coal = fin_qty_coal + q_coal
        qty_coal = float(qty_coal) - q_coal
        fin_qty_ore = fin_qty_ore + q_ore
        qty_ore = float(qty_ore) - q_ore
        fin_qty_copper = fin_qty_copper + q_copper
        qty_copper = float(qty_copper) - q_copper
        fin_qty_uranium = fin_qty_uranium + q_uranium
        qty_uranium = float(qty_uranium) - q_uranium
    
    table = connection["missions"]
    table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "deploy",  "date": time_now, "busy_until": t_arrival,
                  "busy_until_return": None, "ships": json.dumps(ships), "cords_hor": s_cords_hor,
                  "cords_ver": s_cords_ver, "cords_hor_dest": planet_to_data['cords_hor'], "cords_ver_dest": planet_to_data['cords_ver'],
                  "qyt_coal": float(qty_coal), "qyt_ore": float(qty_ore), "qyt_copper": float(qty_copper),
                  "qyt_uranium": float(qty_uranium)})     
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])
    return (True)
    
# VOPS "offload_deploy"
def offload_deploy(shipid, mission_id, parameter, time_now, block_num, trx_id):
    # NOT USED ANYMORE - LEGACY ONLY
    connection = connectdb()
    print("offload_deploy")
    
    (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,tmp_mission_id, home_planet_id) = get_shipdata(shipid)

    #get the data from the planet on which the ship is currently  located
    planet_id = get_planetid (s_cords_hor,s_cords_ver)
    if planet_id is None:
        print("No planet at offload location")
        return False
    print(planet_id)
    table = connection["planets"]
    planet_data = table.find_one(id=planet_id)
    user = planet_data['user']
    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    
    fin_qty_coal = float(new_qty_coal) + float(s_qty_coal)
    fin_qty_ore = float(new_qty_ore) + float(s_qty_ore)
    fin_qty_copper = float(new_qty_copper) + float(s_qty_copper)
    fin_qty_uranium = float(new_qty_uranium) + float(s_qty_uranium)
        
    table = connection['ships']
    table.update({"id": str(shipid), "user": user,
                  "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                  "qyt_uranium": 0},['id'])    
        
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])    

    
    return (True)

# VOPS "offload_deploy_mission"
def offload_deploy_mission(mission_id, planet_id, parameter, time_now, block_num, trx_id):
    # increase the level of resources on the target planet
    upgrade_costs = parameter["upgrade_costs"]
    connection = connectdb()
    print("offload")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    sender = mission_data["user"]

    table = connection["planets"]
    planet_data = table.find_one(id=planet_id)
    if planet_data is None:
        print("No planet at offload location")
        return False    
    user = planet_data['user']
 
    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    fin_qty_coal = float(new_qty_coal)
    fin_qty_ore = float(new_qty_ore)
    fin_qty_copper = float(new_qty_copper)
    fin_qty_uranium = float(new_qty_uranium)
    
    connection.begin()  
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):
        shipid = ship["id"]
        (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,tmp_mission_id, home_planet_id) = get_shipdata(shipid)        
        fin_qty_coal = fin_qty_coal + float(s_qty_coal)
        fin_qty_ore = fin_qty_ore + float(s_qty_ore)
        fin_qty_copper = fin_qty_copper + float(s_qty_copper)
        fin_qty_uranium = fin_qty_uranium + float(s_qty_uranium)
          
        table = connection['ships']
        table.update({"id": str(shipid), "user": user,
                      "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                      "qyt_uranium": 0},['id'])    
    connection.commit()
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])    

    # Update Yamato Ranking for deployed ships
    # Get current season            
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None or last_season["end_date"] < time_now:
        current_season = None
    else:
        current_season = last_season
    if current_season is not None:
        season_id = int(current_season["id"])
        deploy_rate = current_season["deploy_rate"]
        if deploy_rate is not None:
            deploy_rate = float(deploy_rate)
        else:
            deploy_rate = 0
    else:
        season_id = None
        deploy_rate = None 

    if season_id is not None and sender != user:       
        # Get Sender (sender) reward
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=sender)
        if ranking is not None:
            old_sender_build_reward = int(ranking["build_reward"])
            old_sender_total_reward = int(ranking["total_reward"])
        else:
            old_sender_build_reward = 0
            old_sender_total_reward = 0
        # Get Recipient (user) reward        
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=user)
        if ranking is not None:
            old_recipient_build_reward = int(ranking["build_reward"])
            old_recipient_total_reward = int(ranking["total_reward"])
        else:
            old_recipient_build_reward = 0
            old_recipient_total_reward = 0   
        table = connection["ships"]
        delta_build_reward = 0
        for ship in table.find(mission_id=mission_id):
            shipid = ship["id"]
            shiptype = ship["type"]
            if shiptype[:6] == "yamato":
                if shiptype[6:] is not None and shiptype[6:] != "":
                    shiptier = int(shiptype[6:])
                else:
                    continue
                # Loop through all tiers with stardust to sum up total reward to tranfer   
                for tier in range(1, shiptier+1):   
                    current_shiptype = "yamato"+str(tier)             
                    build_costs = upgrade_costs[current_shiptype]['1']
                    if build_costs["stardust"] is not None:
                        delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                    else:
                        delta_build_reward = delta_build_reward + 0
        if delta_build_reward != 0:
            new_sender_build_reward = old_sender_build_reward - delta_build_reward
            new_sender_total_reward = old_sender_total_reward - delta_build_reward     
            table_ranking.upsert({"season_id": season_id, "user": sender, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"])    
        if delta_build_reward != 0 and deploy_rate != 0:      
            new_recipient_build_reward = old_recipient_build_reward + deploy_rate * delta_build_reward            
            new_recipient_total_reward = old_recipient_total_reward + deploy_rate * delta_build_reward    
            table_ranking.upsert({"season_id": season_id, "user": user, "last_update": time_now, "build_reward":new_recipient_build_reward, "total_reward": new_recipient_total_reward}, ["season_id", "user"])   

    return (True)

# VOPS "offload_return_mission"
def offload_return_mission(mission_id, planet_id, parameter, time_now, block_num, trx_id):
    # increase the level of resources on the target planet
    connection = connectdb()
    print("offload_return_mission")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    
    
    shipstats = parameter["shipstats"]
    connection = connectdb()
    print("cancel")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    cords_hor = mission_data["cords_hor"]
    cords_ver = mission_data["cords_ver"]
    
    if time_now < datetime(2019, 7, 17, 5, 30, 0):
        
        planet_id = get_planetid (cords_hor,cords_ver)
        if planet_id is None:
            print("No planet to return to")
            return False
    else:
        return_planet_id = get_planetid (cords_hor,cords_ver)
        if return_planet_id is None:
            print("No planet to return to")
            return False
    
    cords_hor_dest = mission_data["cords_hor_dest"]
    cords_ver_dest = mission_data["cords_ver_dest"]    
    user = mission_data["user"]
    distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
    
    apply_battlespeed = False
    if user is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=user)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    consumption_ship = {}
    qyt_ship_uranium = {}
    ship_list = []
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):
        ship_list.append(ship)
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance, apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        qyt_ship_uranium[ship["id"]] = float(ship["qyt_uranium"]) - consumption
        if qyt_ship_uranium[ship["id"]] < 0:
            print("Resetting negative ship uranium.")
            qyt_ship_uranium[ship["id"]] = 0                       

    print("ships %d found" % len(ship_list))
        
    t_arrival = time_now + timedelta(max_duration / 24)    
    print("Distance %.2f, duration %.2f, arrival %s" % (distance, max_duration, str(t_arrival)))
 
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    fin_qty_coal = float(new_qty_coal)
    fin_qty_ore = float(new_qty_ore)
    fin_qty_copper = float(new_qty_copper)
    fin_qty_uranium = float(new_qty_uranium)

    connection.begin()
    table = connection["missions"]
    table.update({"mission_id": mission_id, "busy_until_return": t_arrival, "returning": True}, ["mission_id"])
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):
        shipid = ship["id"]
        (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,tmp_mission_id, home_planet_id) = get_shipdata(shipid)        
        fin_qty_coal = fin_qty_coal + float(s_qty_coal)
        fin_qty_ore = fin_qty_ore + float(s_qty_ore)
        fin_qty_copper = fin_qty_copper + float(s_qty_copper)
    
        fin_qty_uranium = fin_qty_uranium + float(qyt_ship_uranium[ship["id"]])
             
        table = connection['ships']
        table.update({"id": str(shipid), "user": user, "cords_hor": cords_hor, "cords_ver": cords_ver,
                      "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                      "qyt_uranium": 0, "mission_busy_until": t_arrival},['id'])    
    
    connection.commit()
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])      
    
    return (True)

# VOPS "fly_home_mission"
def fly_home_mission(mission_id, planet_id, parameter, time_now, block_num, trx_id):
    # increase the level of resources on the target planet
    connection = connectdb()
    print("fly_home_mission")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    
    
    shipstats = parameter["shipstats"]
    connection = connectdb()
    print("cancel")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    cords_hor = mission_data["cords_hor"]
    cords_ver = mission_data["cords_ver"]
    
    planet_id = get_planetid (cords_hor,cords_ver)
    if planet_id is None:
        print("No planet to return to")
        return False    
    
    cords_hor_dest = mission_data["cords_hor_dest"]
    cords_ver_dest = mission_data["cords_ver_dest"]    
    user = mission_data["user"]
    mission_type = mission_data["mission_type"]
    distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
    
    apply_battlespeed = False
    if user is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=user)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    consumption_ship = {}
    qyt_ship_uranium = {}
    ship_list = []
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):
        ship_list.append(ship)
        capacity = shipstats[ship["type"]]["capacity"]    
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]], distance,apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        qyt_ship_uranium[ship["id"]] = float(ship["qyt_uranium"]) - consumption
        if qyt_ship_uranium[ship["id"]] < 0:
            print("Resetting negative ship uranium.")
            qyt_ship_uranium[ship["id"]] = 0               

    print("ships %d found" % len(ship_list))
        
    t_arrival = time_now + timedelta(max_duration / 24)    
    print("Distance %.2f, duration %.2f, arrival %s" % (distance, max_duration, str(t_arrival)))  
  
    connection.begin()
    table = connection["missions"]
    table.update({"mission_id": mission_id, "busy_until_return": t_arrival, "returning": True}, ["mission_id"])      

    table = connection["ships"]
    for ship in ship_list:
        shipid = ship["id"]
        table = connection["ships"]
        table.update({"id": str(shipid), "cords_hor": cords_hor, "cords_ver": cords_ver,
                      "qyt_uranium": qyt_ship_uranium[shipid], "mission_busy_until": t_arrival},['id'])
    # write an "offload" transaction into the transactions db, with a time set to the arrival time of the ships
   
    connection.commit()
    print("write vops")
    table = connection["virtualops"]
    table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": planet_id,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":user})         
    
    return True
    
# Command "cancel" 
def cancel(mission_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    connection = connectdb()
    print("cancel")
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    cords_hor = mission_data["cords_hor"]
    cords_ver = mission_data["cords_ver"]
    
    planet_id = get_planetid (cords_hor,cords_ver)
    if planet_id is None:
        print("No planet to return to")
        return False    
    
    cords_hor_dest = mission_data["cords_hor_dest"]
    cords_ver_dest = mission_data["cords_ver_dest"]    
    user = mission_data["user"]
    mission_type = mission_data["mission_type"]

    if mission_type == "upgradeyamato":
        print("Cannot cancel yamato upgrades ...")
        return False
        
    if  (mission_type == "support") and mission_data["busy_until"] < time_now and mission_data["cancel_trx"] is None:
        distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
        total_distance = distance
    elif  (mission_type == "siege") and mission_data["busy_until"] < time_now and mission_data["cancel_trx"] is None:
        distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
        total_distance = distance
        table = connection["virtualops"]
        if table.count(mission_id=mission_id) == 0:
            print("Cannot cancel, no vops was found.")
            return False    
        vops_id_list = []
        for vops in table.find(mission_id=mission_id):
            vops_id_list.append(vops["id"])
        for vops_id in vops_id_list:
            table.update({"id": vops_id, "tr_status": 3}, ["id"])        
        
    elif (mission_type == "support") and mission_data["busy_until"] > time_now and mission_data["cancel_trx"] is None:
        trigger_date = mission_data["busy_until"]
        start_date = mission_data["date"]
        total_flight_duration_s = (trigger_date - start_date).total_seconds()
        flight_duration_s = (time_now - start_date).total_seconds()
        total_distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
        distance = total_distance * flight_duration_s / total_flight_duration_s        
    else:
        
        if mission_data["busy_until"] < time_now and mission_type != "siege":
            print("Cannot cancel, already flying back...")
            return False
        if mission_data["cancel_trx"] is not None:
            print("Cannot cancel, already canceled...")
            return False            
        table = connection["virtualops"]
        if table.count(mission_id=mission_id) == 0:
            print("Cannot cancel, no vops was found.")
            return False    
        vops_id_list = []
        for vops in table.find(mission_id=mission_id):
            vops_id_list.append(vops["id"])
        if time_now < datetime(2019, 7, 13, 15, 0, 0):
            table = connection["virtualops"]
            for vops_id in vops_id_list:
                table.update({"id": vops_id, "tr_status": 3}, ["id"])
        trigger_date = vops["trigger_date"]
        start_date = vops["date"]
        total_flight_duration_s = (trigger_date - start_date).total_seconds()
        flight_duration_s = (time_now - start_date).total_seconds()
        total_distance = get_distance(cords_hor,cords_ver,cords_hor_dest,cords_ver_dest)
        distance = total_distance * flight_duration_s / total_flight_duration_s
        
    
    apply_battlespeed = False
    if user is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=user)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True   

    max_duration = 0
    consumption_ship = {}
    qyt_ship_uranium = {}
    ship_list = []
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):
        ship_list.append(ship) 
        (total_consumption, total_flight_duration) = get_flight_param(shipstats[ship["type"]], total_distance, apply_battlespeed)
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]], distance, apply_battlespeed)
        uranium_in_tank = total_consumption - consumption
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        qyt_ship_uranium[ship["id"]] = float(ship["qyt_uranium"]) - consumption + uranium_in_tank
        if qyt_ship_uranium[ship["id"]] < 0:
            if mission_type == "deploy":
                print("Cannot cancel, not sufficient uranium for flying back.")
                return False
            else:
                print("Not enough uranium to fly back. Use the invisible reserve tank.")
                qyt_ship_uranium[ship["id"]] = 0
    print("ships %d found" % len(ship_list))
        
    t_arrival = time_now + timedelta(max_duration / 24)    
    print("Distance %.2f, duration %.2f, arrival %s" % (distance, max_duration, str(t_arrival)))
    
    if time_now > datetime(2019, 7, 14, 16, 30, 0):
        table = connection["virtualops"]
    
    vops_id_list = []
    for vops in table.find(mission_id=mission_id):
        vops_id_list.append(vops["id"])
    if time_now >= datetime(2019, 7, 13, 15, 0, 0):
        table = connection["virtualops"]
        for vops_id in vops_id_list:
            table.update({"id": vops_id, "tr_status": 3}, ["id"])    
    
    table = connection["missions"]
    table.update({"mission_id": mission_id, "busy_until": t_arrival, "busy_until_return": None, "returning": True,
                  "cancel_trx": trx_id}, ["mission_id"])        
    table = connection["activity"]
    if mission_type == "support" and mission_data["busy_until"] < time_now:
        table.upsert({"user": user, "mission_id": mission_id, "type": mission_data["mission_type"], "date": time_now,  "cords_hor": int(cords_hor_dest),
                      "cords_ver": int(cords_ver_dest), "result": "cancel_support"}, ["mission_id"])    
    else:
        table.upsert({"user": user, "mission_id": mission_id, "type": mission_data["mission_type"], "date": time_now,  "cords_hor": int(cords_hor_dest),
                      "cords_ver": int(cords_ver_dest), "result": "cancel"}, ["mission_id"])     
    connection.begin()
    table = connection["ships"]
    for ship in ship_list:
        shipid = ship["id"]
        table = connection["ships"]
        table.update({"id": str(shipid), "cords_hor": cords_hor, "cords_ver": cords_ver,
                      "qyt_uranium": qyt_ship_uranium[shipid], "mission_busy_until": t_arrival},['id'])
    # write an "offload" transaction into the transactions db, with a time set to the arrival time of the ships
   
    connection.commit()
    print("write vops")
    table = connection["virtualops"]
    table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": planet_id,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":user})         
    
    return True

# VOPS "battle_return"
def battle_return(mission_id, to_planet_id, attack_mission_type, parameter, time_now, block_num, trx_id):
    
    shipstats = parameter["shipstats"]
    upgrade_costs = parameter["upgrade_costs"]
    connection = connectdb()
    print("battle_return")
        
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)
    
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False
    cords_hor = mission_data["cords_hor"]
    cords_ver = mission_data["cords_ver"]    
    cords_hor_dest = mission_data["cords_hor_dest"]
    cords_ver_dest = mission_data["cords_ver_dest"]
    user = mission_data["user"]
    
    table = connection["users"]
    attacker = table.find_one(username=user)
    
    if attacker["r_rocketimprove"] is None:
        a_roi = 1
    else:
        a_roi = 1 + (int(attacker["r_rocketimprove"]) / 100)
    if attacker["r_bulletimprove"] is None:
        a_bui = 1
    else:
        a_bui = 1 + (int(attacker["r_bulletimprove"]) / 100)               
    if attacker["r_laserimprove"] is None:
        a_lai = 1
    else:
        a_lai = 1 + (int(attacker["r_laserimprove"]) / 100)
        
    if attacker["r_structureimprove"] is None:
        a_sti = 1
    else:
        a_sti = 1 + (int(attacker["r_structureimprove"]) / 100)                  
    if attacker["r_armorimprove"] is None:
        a_ari = 1
    else:
        a_ari = 1 + (int(attacker["r_armorimprove"]) / 100)  
    if attacker["r_shieldimprove"] is None:
        a_shi = 1
    else:
        a_shi = 1 + (int(attacker["r_shieldimprove"]) / 100)         
    
    #get the data from the planet on which the ship is currently  located
    planet_id = get_planetid (cords_hor_dest,cords_ver_dest)
    if planet_id is None:
        print("No planet at battle location")
        return False
    print(planet_id)
    default_pos = {"Yamato": 1, "Scout": 2, "Patrol": 3, "Cutter": 4, "Corvette": 5, "Frigate": 6, "Destroyer": 7, "Cruiser": 8, "Battlecruiser": 9,
                   "Carrier": 10, "Dreadnought": 11, "Transporter": 12, "Explorer": 13 }
    
    table = connection["planets"]
    planet_data = table.find_one(id=planet_id)
    opponent = planet_data['user']
    bunker_level = planet_data['level_bunker']
    coaldepot_size = float(planet_data['depot_coal'])
    oredepot_size = float(planet_data['depot_ore'])
    copperdepot_size = float(planet_data['depot_copper'])
    uraniumdepot_size = float(planet_data['depot_uranium'])    
    if bunker_level is None or bunker_level == 0:
        bunker_level = 0
   
    shieldprotection_busy = planet_data["shieldprotection_busy"]
    if shieldprotection_busy is None:
        shieldprotection_busy = datetime(1990,1,1,1,1,1,1)    
    
    table = connection["users"]
    defender = table.find_one(username=opponent)
    enlargebunker_level = defender['r_enlargebunker']
    if enlargebunker_level is None:
        enlargebunker_level = 0    
    bunker_protection = (bunker_level * 0.005 + 0.05 + enlargebunker_level * 0.0025)
    if bunker_level == 0:
        bunker_protection = 0
    coalsafe = coaldepot_size * bunker_protection
    oresafe = oredepot_size * bunker_protection
    coppersafe = copperdepot_size * bunker_protection
    uraniumsafe = uraniumdepot_size * bunker_protection    
    
    
    attacker_ship_list = []
    attacker_by_type = {}
    attacker_stats = {}
    initial_attacker_stats = {}
    attack_sum = 0
    table = connection["ships"]
    for ship in table.find(mission_id=mission_id):

        attacker_ship_list.append(ship)
        shipclass = shipstats[ship["type"]]["class"]
        if ship["position"] is None and shipclass in default_pos:
            position = default_pos[shipclass]
        elif ship["position"] is None:
            position = 8
        else:
            position = ship["position"]            
        if ship["type"] in attacker_by_type:
            attacker_by_type[ship["type"]]["n"] += 1
        else:
            attacker_by_type[ship["type"]] = {"n": 1, "lost": 0, "pos": position, "class": shipclass, "type": ship["type"]}

    attacker_list = []
    for shiptype in attacker_by_type:
        attacker_list.append(attacker_by_type[shiptype])
    
    attacker_list_sorted = sorted(attacker_list, key=lambda d: d["pos"], reverse=False)

    ship_index = 1
    ship_positions = []
    for ship in attacker_list_sorted:
        shiptype = ship["type"]
        n = attacker_by_type[shiptype]["n"]
        position = attacker_by_type[shiptype]["pos"]
        shipclass = attacker_by_type[shiptype]["class"]
        if position is None:
            position = 1
        while position in ship_positions and position <= 8:
            position += 1
        if position == 9:
            position = 1
            while position in ship_positions and position < 8:
                position += 1         
        st = shipstats[shiptype]
        if position not in ship_positions:
            attack_sum += n*st["bullet"] + n*st["laser"] + n*st["rocket"]
            ship_positions.append(position)
            for i in range(n):
                attacker_stats[ship_index] = {"n": 1, "lost": 0, "survivor": 1, "structure": st["structure"] * a_sti, "armor": st["armor"] * a_ari,
                                             "shield": st["shield"] * a_shi, "rocket": st["rocket"] * a_roi,
                                             "bullet": st["bullet"] * a_bui, "laser": st["laser"] * a_lai, "position": position,
                                             "class": shipclass, "type": shiptype, "longname": shipstats[shiptype]["longname"]}
                ship_index += 1

            initial_attacker_stats[position] = {"n": n, "lost": 0, "survivor": n, "structure": n*st["structure"] * a_sti, "armor": n*st["armor"] * a_ari,
                                             "shield": n*st["shield"] * a_shi, "rocket": n*st["rocket"] * a_roi, "position": position,
                                             "bullet": n*st["bullet"] * a_bui, "laser": n*st["laser"] * a_lai,
                                             "class": shipclass, "type": shiptype, "longname": shipstats[shiptype]["longname"]}
            
            
            
    print("Attacker %s" % str(attacker_by_type))
    
    # support missions
    table = connection["missions"]
    defender_type_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=cords_hor_dest, cords_ver_dest=cords_ver_dest, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now:
            continue
        defender_type_list.append({"mission_id": mission["mission_id"], "user": mission["user"], "mission_type": "siege"})    
    for mission in table.find(mission_type="support", cords_hor_dest=cords_hor_dest, cords_ver_dest=cords_ver_dest, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if cords_hor == cords_hor_dest and cords_ver == cords_ver_dest:
            continue
        if attack_mission_type == "siege":
            continue
        defender_type_list.append({"mission_id": mission["mission_id"], "user": mission["user"], "mission_type": "support"})
    for mission in table.find(mission_type="upgradeyamato", cords_hor_dest=cords_hor_dest, cords_ver_dest=cords_ver_dest, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now:
            continue
        if cords_hor == cords_hor_dest and cords_ver == cords_ver_dest:
            continue
        if attack_mission_type == "siege":
            continue
        defender_type_list.append({"mission_id": mission["mission_id"], "user": mission["user"], "mission_type": "upgradeyamato"})
    if cords_hor != cords_hor_dest or cords_ver != cords_ver_dest or attack_mission_type != "siege":
        defender_type_list.append({"user": opponent})
    print("Defending missions found: %s" % str(defender_type_list))

    attacker_ship_delete = []
    attacker_ship_downgrade = []
    attacker_ship_delete_by_opponent = {}
    defender_ship_delete = []
    defender_ship_downgrade = []
    defence_mission_ids = []
    battle_number = 1
    attacker_result = -1
    defender_result = -1

    ########################################
    # START OF BATTLING EACH DEFENDER
    ########################################     
    for defender_type in defender_type_list:
    
        if user == defender_type["user"]:
            attacker_result = 2
            defender_result = 1
            initial_defender_stats = {}
            defender_stats = {}
            print("Skip %s vs %s" % (user, defender_type["user"]))
            continue
        
        table = connection["users"]
        defender = table.find_one(username=defender_type["user"])
        
        if defender["r_rocketimprove"] is None:
            d_roi = 1
        else:
            d_roi = 1 + (int(defender["r_rocketimprove"]) / 100)
            
        if defender["r_bulletimprove"] is None:
            d_bui = 1
        else:
            d_bui = 1 + (int(defender["r_bulletimprove"]) / 100)               
        if defender["r_laserimprove"] is None:
            d_lai = 1
        else:
            d_lai = 1 + (int(defender["r_laserimprove"]) / 100)
            
        if defender["r_structureimprove"] is None:
            d_sti = 1
        else:
            d_sti = 1 + (int(defender["r_structureimprove"]) / 100)               
        if defender["r_armorimprove"] is None:
            d_ari = 1
        else:
            d_ari = 1 + (int(defender["r_armorimprove"]) / 100)  
        if defender["r_shieldimprove"] is None:
            d_shi = 1
        else:
            d_shi = 1 + (int(defender["r_shieldimprove"]) / 100) 
        
        defender_ship_list = []
        defender_by_type = {}
        defence_mission_type = "planet"
        if "mission_id" in defender_type:
            defence_mission_ids.append(defender_type["mission_id"])
            defence_mission_type = defender_type["mission_type"]
        
        table = connection["ships"]
        for ship in table.find(cords_hor=cords_hor_dest, cords_ver=cords_ver_dest, user={'not': user}):
            if ship["busy_until"] > time_now:
                continue
            if defence_mission_type != "upgradeyamato":
                if ship["mission_busy_until"] is not None and ship["mission_busy_until"] > time_now:
                    continue
            if ship["id"] in defender_ship_delete:
                continue
            if "mission_id" in defender_type:
                if ship["mission_id"] != defender_type["mission_id"]:
                    continue
            else:
                if ship["user"] != defender_type["user"]:
                    continue
                if ship["mission_id"] in defence_mission_ids:
                    continue
            defender_ship_list.append(ship)
            shipclass = shipstats[ship["type"]]["class"]
            st = shipstats[ship["type"]]
            attack = st["bullet"] + st["laser"] + st["rocket"]
            if ship["position"] is None and shipclass in default_pos:
                position = default_pos[shipclass]
            elif ship["position"] is None:
                position = 8
            else:
                position = ship["position"]
            if ship["type"] in defender_by_type:
                defender_by_type[ship["type"]]["n"] += 1
                defender_by_type[ship["type"]]["attack"] += attack
            else:
                defender_by_type[ship["type"]] = {"n": 1, "lost": 0, "pos": position, "class": shipclass, "type": ship["type"], "attack": attack}
        
        defender_list = []
        for shiptype in defender_by_type:
            defender_list.append(defender_by_type[shiptype])
        
        defender_list_sorted = sorted(defender_list, key=lambda d: d["pos"], reverse=False)
        print(defender_list_sorted)
        defender_stats = {}
        initial_defender_stats = {}
        defend_sum = 0
        ship_index = 1
        ship_positions = []
        position = 1
        for shiptype in defender_list_sorted:
            n = shiptype["n"]
            shipclass = shiptype["class"]
            while position in ship_positions:
                position += 1
            print(shiptype["type"])
            st = shipstats[shiptype["type"]]
            
            if position not in ship_positions:
                ship_positions.append(position)
                defend_sum += n*st["bullet"] + n*st["laser"] + n*st["rocket"]
                for i in range(n):
                    
                    defender_stats[ship_index] = {"n": 1, "lost": 0, "survivor": 1, "structure": st["structure"] * d_sti, "armor": st["armor"] * d_ari,
                                                 "shield": st["shield"] * d_shi, "rocket": st["rocket"] * d_roi,
                                                 "bullet": st["bullet"] * d_bui, "laser": st["laser"] * d_lai, "position": position,
                                                 "class": shipclass, "type": shiptype["type"], "longname": shipstats[shiptype["type"]]["longname"]}
                    ship_index += 1
                initial_defender_stats[position] = {"n": n, "lost": 0, "survivor": n, "structure": n*st["structure"] * d_sti, "armor": n*st["armor"] * d_ari,
                                                 "shield": n*st["shield"] * d_shi, "rocket": n*st["rocket"] * d_roi,
                                                 "bullet": n*st["bullet"] * d_bui, "laser": n*st["laser"] * d_lai, "position": position,
                                                 "class": shipclass, "type": shiptype["type"], "longname": shipstats[shiptype["type"]]["longname"]}
        print("Defender %s" % str(defender_by_type))
        # print("Defender stats %s" % str(defender_stats))
        attacker_result = -1
        defender_result = -1
        
        
        if defend_sum == 0 and attack_sum == 0 and len(defender_ship_list) > 0:
            attacker_result = 0
            defender_result = 0
            print("no defender and no attacker")
        # Special case when attacker gets destroyed by support and there is no defenders on the planet
        elif len(defender_ship_list) == 0 and len(attacker_ship_list) > 0 and len(attacker_stats) == 0: 
            attacker_result = 1
            defender_result = 2
            print("no attacker left and no defender on the planet")   
        elif len(defender_ship_list) == 0 and len(attacker_ship_list) > 0: 
            attacker_result = 2
            defender_result = 1
            print("no defender")    
        elif len(defender_ship_list) == 0 and len(attacker_ship_list) == 0: 
            attacker_result = 0
            defender_result = 0
            print("no defender and no attacker")             
        else:
            attacker_result = 0
            defender_result = 0        
            print("start to fight")
            turn = 'Attacker'
            currentAttacker = 1
            battle_round = 1
            currentDefender = 1
            currentAttackerShooter = 1
            currentDefenderShooter = 1
            previousTank = 1
            previousShooter = 1
            
            game_finished = False
            
            
            rates = {}
            rates["rocket"] = {}
            rates["laser"] = {}
            rates["bullet"] = {}

            rates["rocket"]["structure"] = 4
            rates["rocket"]["armor"] = 2
            rates["rocket"]["shield"] = 1
            rates["laser"]["structure"] = 2
            rates["laser"]["armor"] = 1
            rates["laser"]["shield"] = 4     
            rates["bullet"]["structure"] = 1
            rates["bullet"]["armor"] = 4
            rates["bullet"]["shield"] = 2                

            while not game_finished:
                print("round %d - %s" % (battle_round, turn))
                
                maxAttackerShooterReached = False
                maxDefenderShooterReached = False
                
                attacker_found = False
                previousTank  = currentAttacker
                previousShooter  = currentAttackerShooter
                # Find the next surviving attacker
                for searchedAttacker in attacker_stats:
                    if currentAttacker == searchedAttacker and attacker_stats[searchedAttacker]["structure"] > 0:
                        attacker_found = True
                        break
                    if currentAttacker < searchedAttacker and attacker_stats[searchedAttacker]["structure"] > 0:
                        currentAttacker = searchedAttacker
                        if previousTank == previousShooter:
                            currentAttackerShooter = currentAttacker
                        attacker_found = True
                        break
                        
                if not attacker_found:
                    print("attacker has lost")
                    attacker_result = 1
                    defender_result = 2
                    game_finished = True
                    continue   

                defender_found = False
                search_round = 0
                while not defender_found and search_round < 2:
                    if currentDefender in defender_stats and defender_stats[currentDefender]["structure"] > 0:
                        defender_found = True
                        continue
                    
                    previousTank  = currentDefender
                    previousShooter  = currentDefenderShooter
                    if (currentDefender + 1) in defender_stats:
                        currentDefender += 1
                        if previousTank  == previousShooter:
                            currentDefenderShooter = currentDefender
                    else:
                        search_round += 1
                            
                if not defender_found:
                    print("defender has lost")
                    attacker_result = 2
                    defender_result = 1                
                    game_finished = True
                    continue                 
        
                print("Attacker: %d - %d, Defender %d - %d" % (currentAttackerShooter, currentAttacker, currentDefenderShooter, currentDefender))
                if turn == "Attacker":
                    if attacker_stats[currentAttackerShooter]["structure"] > 0:
                        
                        leftOver = { "laser": 0, "bullet": 0, "rocket": 0 }
                        defender_stats, leftOver = apply_damage(defender_stats, currentDefender, attacker_stats, currentAttackerShooter, defender, leftOver, rates, shipstats, battle_round, time_now)
                        while (leftOver["laser"] > 0 or leftOver["bullet"] > 0 or leftOver["rocket"] > 0):
                            defender_found = False
                            search_round = 0
                            while not defender_found and search_round < 2:
                                if currentDefender in defender_stats and defender_stats[currentDefender]["structure"] > 0:
                                    defender_found = True
                                    continue
                                
                                if (currentDefender + 1) in defender_stats:
                                    currentDefender += 1
                                else:
                                    search_round += 1

                            if not defender_found:
                                leftOver = { "laser": 0, "bullet": 0, "rocket": 0 }
                            else:
                                defender_stats, leftOver = apply_damage(defender_stats, currentDefender, attacker_stats, currentAttackerShooter, defender, leftOver, rates, shipstats, battle_round, time_now)
                        
                        
                elif turn == "Defender":
                    
                    leftOver = { "laser": 0, "bullet": 0, "rocket": 0 }
                    attacker_stats, leftOver = apply_damage(attacker_stats, currentAttacker, defender_stats, currentDefenderShooter, attacker, leftOver, rates, shipstats, battle_round, time_now)
                    while (leftOver["laser"] > 0 or leftOver["bullet"] > 0 or leftOver["rocket"] > 0):
                        attacker_found = False
                        search_round = 0
                        while not attacker_found and search_round < 2:
                            if currentAttacker in attacker_stats and attacker_stats[currentAttacker]["structure"] > 0:
                                attacker_found = True
                                continue
                            
                            if (currentAttacker + 1) in attacker_stats:
                                currentAttacker += 1
                            else:
                                search_round += 1

                        if not attacker_found:
                            leftOver = { "laser": 0, "bullet": 0, "rocket": 0 }
                        else:
                            attacker_stats, leftOver = apply_damage(attacker_stats, currentAttacker, defender_stats, currentDefenderShooter, attacker, leftOver, rates, shipstats, battle_round, time_now)
                
                if defender_stats[currentDefender]["structure"] == 0:
                    print("attacker won round")
                if attacker_stats[currentAttacker]["structure"] == 0:
                    print("defender won round")
                if turn == "Attacker":
                    currentAttackerShooter += 1
                    attacker_found = False
                    while not attacker_found and currentAttackerShooter < len(attacker_stats) + 1:
                        if currentAttackerShooter in attacker_stats and attacker_stats[currentAttackerShooter]["structure"] > 0:
                            attacker_found = True
                            continue
                        currentAttackerShooter += 1                    
                if currentAttackerShooter not in attacker_stats:
                    maxAttackerShooterReached = True
                    
                if turn == "Defender":
                    currentDefenderShooter += 1
                    defender_found = False
                    while not defender_found and currentDefenderShooter < len(defender_stats) + 1:
                        if currentDefenderShooter in defender_stats and defender_stats[currentDefenderShooter]["structure"] > 0:
                            defender_found = True
                            continue
                        currentDefenderShooter += 1     
                if currentDefenderShooter not in defender_stats:
                    maxDefenderShooterReached = True

                if turn == "Attacker":
                    turn = "Defender"
                else:
                    turn = "Attacker"
                          
                if maxAttackerShooterReached and maxDefenderShooterReached:
                    currentDefenderShooter = currentDefender
                    currentAttackerShooter  = currentAttacker
                elif maxAttackerShooterReached: 
                    turn = "Defender"
                elif maxDefenderShooterReached:
                    turn = "Attacker"
                    
                battle_round += 1
                
        
        attacker_ship_lost = {}
        for pos in attacker_stats:
            if attacker_stats[pos]["lost"] == 0:
                continue
            if attacker_stats[pos]["type"] not in attacker_ship_lost:
                attacker_ship_lost[attacker_stats[pos]["type"]] = attacker_stats[pos]["lost"]
            elif time_now > datetime(2019, 8, 14, 12, 17, 0):
                attacker_ship_lost[attacker_stats[pos]["type"]] += attacker_stats[pos]["lost"]
         
        for ship in attacker_ship_list:
            if ship["type"] in attacker_ship_lost and attacker_ship_lost[ship["type"]] > 0:
                attacker_ship_delete.append(ship["id"])
                if ship["type"][:6] == "yamato" and ship["type"][6:] is not None and ship["type"][6:] != "":
                    attacker_ship_downgrade.append(ship["id"])
                attacker_ship_lost[ship["type"]] -= 1
                if defender_type["user"] not in attacker_ship_delete_by_opponent:
                    attacker_ship_delete_by_opponent[defender_type["user"]] = [ship["id"]]
                else:
                    attacker_ship_delete_by_opponent[defender_type["user"]].append(ship["id"])
    
        defender_ship_lost = {}
        for pos in defender_stats:
            if defender_stats[pos]["lost"] == 0:
                continue
            if defender_stats[pos]["type"] not in defender_ship_lost:
                defender_ship_lost[defender_stats[pos]["type"]] = defender_stats[pos]["lost"]
            elif time_now > datetime(2019, 8, 14, 12, 17, 0):
                defender_ship_lost[defender_stats[pos]["type"]] += defender_stats[pos]["lost"]
        
        
        for ship in defender_ship_list:
            if ship["type"] in defender_ship_lost and defender_ship_lost[ship["type"]] > 0:
                defender_ship_delete.append(ship["id"])
                if ship["type"][:6] == "yamato" and ship["type"][6:] is not None and ship["type"][6:] != "":
                    defender_ship_downgrade.append(ship["id"])
                defender_ship_lost[ship["type"]] -= 1     

        if "mission_id" in defender_type:
            
            if defender["r_regenerationbonus"] is None:
                d_shieldregen = 0
            else:
                d_shieldregen = int(defender["r_regenerationbonus"]) / 200
            if defender["r_repairbonus"] is None:
                d_armorrep = 0
            else:
                d_armorrep = int(defender["r_repairbonus"]) / 200
                
            if attacker["r_regenerationbonus"] is None:
                a_shieldregen = 0
            else:
                a_shieldregen = int(attacker["r_regenerationbonus"]) / 200.
            if attacker["r_repairbonus"] is None:
                a_armorrep = 0.1
            else:
                a_armorrep = int(attacker["r_repairbonus"]) / 200.   

            if len(attacker_stats) > 0 and len(defender_stats) > 0:
                attacker_stats_results = {}
                for pos in attacker_stats:
                    ship = attacker_stats[pos]
                    if ship["position"] not in attacker_stats_results:
                        attacker_stats_results[ship["position"]] = ship.copy()
                    else:
                        attacker_stats_results[ship["position"]]["n"] += ship["n"]
                        attacker_stats_results[ship["position"]]["lost"] += ship["lost"]
                        attacker_stats_results[ship["position"]]["survivor"] += ship["survivor"]
                        attacker_stats_results[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                        attacker_stats_results[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                        attacker_stats_results[ship["position"]]["shield"] += ship["shield"] * ship["survivor"]         
                        attacker_stats_results[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                        attacker_stats_results[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                        attacker_stats_results[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]   

                defender_stats_results = {}
                for pos in defender_stats:
                    ship = defender_stats[pos]
                    if ship["position"] not in defender_stats_results:
                        defender_stats_results[ship["position"]] = ship.copy()
                    else:
                        defender_stats_results[ship["position"]]["n"] += ship["n"]
                        defender_stats_results[ship["position"]]["lost"] += ship["lost"]
                        defender_stats_results[ship["position"]]["survivor"] += ship["survivor"]   
                        defender_stats_results[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                        defender_stats_results[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                        defender_stats_results[ship["position"]]["shield"] += ship["shield"] * ship["survivor"]           
                        defender_stats_results[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                        defender_stats_results[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                        defender_stats_results[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]                        
            
            if "mission_id" in defender_type:
                support_mission_id = defender_type["mission_id"]
                table = connection["battleresults"]
                support_battle_number = table.count(mission_id=support_mission_id) + 1
                if len(attacker_stats) > 0 and len(defender_stats) > 0:
                
                    table = connection["battleresults"]
                    table.upsert({"mission_id": support_mission_id, "battle_number": support_battle_number, "attacker": user, "defender": defender_type["user"], "date": time_now, "trx_id": trx_id, "result": attacker_result,
                                  "initial_attacker_ships": json.dumps(initial_attacker_stats), "final_attacker_ships": json.dumps(attacker_stats_results),
                                  "initial_defender_ships": json.dumps(initial_defender_stats), "final_defender_ships": json.dumps(defender_stats_results),
                                  "coal": 0, "ore": 0, "copper": 0, "uranium": 0, "cords_hor_dest": cords_hor_dest,
                                  "cords_ver_dest": cords_ver_dest, "cords_hor": cords_hor, "cords_ver": cords_ver,  "attacker_shieldregen": a_shieldregen,
                                  "defender_shieldregen": d_shieldregen, "attacker_armorrep": a_armorrep, "support_mission_id": support_mission_id,
                                  "defender_armorrep": d_armorrep}, ["mission_id", "battle_number"])
                    table = connection["activity"]
                    table.upsert({"user": defender_type["user"], "mission_id": support_mission_id, "type": "battle", "date": time_now,  "cords_hor": int(cords_hor_dest),
                                  "cords_ver": int(cords_ver_dest), "result": str(defender_result)}, ["mission_id"])    
                    
            else:
                support_mission_id = None
            if len(attacker_stats) > 0 and len(defender_stats) > 0:
                table = connection["battleresults"]
                table.upsert({"mission_id": mission_id, "battle_number": battle_number, "attacker": user, "defender": defender_type["user"], "date": time_now, "trx_id": trx_id, "result": attacker_result,
                              "initial_attacker_ships": json.dumps(initial_attacker_stats), "final_attacker_ships": json.dumps(attacker_stats_results),
                              "initial_defender_ships": json.dumps(initial_defender_stats), "final_defender_ships": json.dumps(defender_stats_results),
                              "coal": 0, "ore": 0, "copper": 0, "uranium": 0, "cords_hor_dest": cords_hor_dest,
                              "cords_ver_dest": cords_ver_dest, "cords_hor": cords_hor, "cords_ver": cords_ver,  "attacker_shieldregen": a_shieldregen,
                              "defender_shieldregen": d_shieldregen, "attacker_armorrep": a_armorrep, "support_mission_id": support_mission_id,
                              "defender_armorrep": d_armorrep}, ["mission_id", "battle_number"])
                battle_number += 1
            delete_ship_types = []
            # Generate attacker_stats for next battle_number
            for currentAttacker in attacker_stats:
                st = shipstats[attacker_stats[currentAttacker]["type"]]
                if attacker_stats[currentAttacker]["survivor"] == 0:
                    delete_ship_types.append(currentAttacker)
                attacker_stats[currentAttacker]["n"] = attacker_stats[currentAttacker]["survivor"]
                attacker_stats[currentAttacker]["lost"] = 0
                attacker_stats[currentAttacker]["laser"] = attacker_stats[currentAttacker]["survivor"] * st["laser"] * a_lai
                attacker_stats[currentAttacker]["bullet"] = attacker_stats[currentAttacker]["survivor"] * st["bullet"] * a_bui
                attacker_stats[currentAttacker]["rocket"] = attacker_stats[currentAttacker]["survivor"] * st["rocket"] * a_roi
                attacker_stats[currentAttacker]["lost"] = attacker_stats[currentAttacker]["n"] - attacker_stats[currentAttacker]["survivor"]
                attacker_stats[currentAttacker]["structure"] = attacker_stats[currentAttacker]["survivor"] * st["structure"] * a_sti
                attacker_stats[currentAttacker]["armor"] = st["armor"] * a_ari * attacker_stats[currentAttacker]["survivor"]
                attacker_stats[currentAttacker]["shield"] = st["shield"] * a_shi * attacker_stats[currentAttacker]["survivor"]
            # Generate results to be displayed as final state in report
            attacker_stats_results = {}
            for pos in attacker_stats:
                ship = attacker_stats[pos]
                if ship["position"] not in attacker_stats_results:
                    attacker_stats_results[ship["position"]] = ship.copy()
                else:
                    attacker_stats_results[ship["position"]]["n"] += ship["n"]
                    attacker_stats_results[ship["position"]]["lost"] += ship["lost"]
                    attacker_stats_results[ship["position"]]["survivor"] += ship["survivor"]
                    attacker_stats_results[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                    attacker_stats_results[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                    attacker_stats_results[ship["position"]]["shield"] += ship["shield"] * ship["survivor"]         
                    attacker_stats_results[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                    attacker_stats_results[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                    attacker_stats_results[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]               
            # Remove deleted ships
            for currentAttacker in delete_ship_types:
                del(attacker_stats[currentAttacker])
            # Update Initial Ship list for next battle number
            initial_attacker_stats = {}
            for pos in attacker_stats:
                ship = attacker_stats[pos]
                if ship["position"] not in initial_attacker_stats:
                    initial_attacker_stats[ship["position"]] = ship.copy()
                else:
                    initial_attacker_stats[ship["position"]]["n"] += ship["n"]
                    initial_attacker_stats[ship["position"]]["lost"] += ship["lost"]
                    initial_attacker_stats[ship["position"]]["survivor"] += ship["survivor"]
                    initial_attacker_stats[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                    initial_attacker_stats[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                    initial_attacker_stats[ship["position"]]["shield"] += ship["shield"] * ship["survivor"]         
                    initial_attacker_stats[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                    initial_attacker_stats[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                    initial_attacker_stats[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]                       

    ########################################
    # END OF BATTLING EACH DEFENDER
    ########################################    
    
    table = connection["planets"]
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
    planet_to_owner = planet_to_data['user']
  
    distance = get_distance(cords_hor_dest,cords_ver_dest,planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    if attacker_result == 1:
        if not attacker_ship_downgrade:
            table = connection["missions"]
            table.update({"mission_id": mission_id,  "date": time_now, "busy_until_return": time_now}, ["mission_id"])            

    apply_battlespeed = False
    if user is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=user)
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True              

    table = connection["ships"]
    max_duration = 0
    free_capacity = 0
    uranium_consumption = 0    
    consumption_ship = {}
    ship_list = []
    flight_duration = 0
    for ship in table.find(mission_id=mission_id):
        if ship["id"] in attacker_ship_delete and ship["id"] not in attacker_ship_downgrade:
            continue
        # calculate the arrival time of the ships
        ship_list.append(ship)
        capacity = shipstats[ship["type"]]["capacity"]    
        
        (consumption, flight_duration) = get_flight_param(shipstats[ship["type"]],distance,apply_battlespeed)
        if max_duration < flight_duration:
            max_duration = flight_duration
        consumption_ship[ship["id"]] = consumption
        uranium_consumption += consumption
        free_capacity += float(capacity)
        
    t_arrival = time_now + timedelta(max_duration / 24)
    
    # get resources of the attacked planet
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    q_coal = float(new_qty_coal)
    q_ore = float(new_qty_ore)
    q_copper = float(new_qty_copper)
    q_uranium = float(new_qty_uranium)
    res_by_ship = {}
    # Calculate resources to be stolen
    if attacker_result == 2:        
        for ship in attacker_ship_list:
            if ship["id"] in attacker_ship_delete and ship["id"] not in attacker_ship_downgrade:
                continue            
            shipid = ship["id"]
            table = connection['ships']
            capacity = shipstats[ship["type"]]["capacity"]
            s_cap = 0
            s_qyt_coal = 0
            s_qyt_ore = 0
            s_qyt_copper = 0
            s_qyt_uranium = 0
            if shieldprotection_busy < time_now and attack_mission_type != "siege":
                if s_cap < float(capacity) and q_uranium > 0:
                    s_qyt_uranium = max(min(q_uranium, float(capacity) - s_cap), 0)
                    if q_uranium - s_qyt_uranium < uraniumsafe:
                        s_qyt_uranium = q_uranium - uraniumsafe
                    if s_qyt_uranium < 0:
                        s_qyt_uranium = 0
                    s_cap += s_qyt_uranium
                    q_uranium -= s_qyt_uranium
                if s_cap < float(capacity) and q_copper > 0:
                    s_qyt_copper = max(min(q_copper, float(capacity) - s_cap), 0)
                    if q_copper - s_qyt_copper < coppersafe:
                        s_qyt_copper = q_copper - coppersafe
                    if s_qyt_copper < 0:
                        s_qyt_copper = 0
                    s_cap += s_qyt_copper
                    q_copper -= s_qyt_copper            
                if s_cap < float(capacity) and q_ore > 0:
                    s_qyt_ore = max(min(q_ore, float(capacity) - s_cap), 0)
                    if q_ore - s_qyt_ore < oresafe:
                        s_qyt_ore = q_ore - oresafe
                    if s_qyt_ore < 0:
                        s_qyt_ore = 0                
                    s_cap += s_qyt_ore         
                    q_ore -= s_qyt_ore                
                if s_cap < float(capacity) and q_coal > 0:
                    s_qyt_coal = max(min(q_coal, float(capacity) - s_cap), 0)
                    if q_coal - s_qyt_coal < coalsafe:
                        s_qyt_coal = q_coal - coalsafe
                    if s_qyt_coal < 0:
                        s_qyt_coal = 0                
                    s_cap += s_qyt_coal
                    q_coal -= s_qyt_coal
            if attack_mission_type != "siege":
                res_by_ship[shipid] = {"uranium": s_qyt_uranium, "copper": s_qyt_copper, "ore": s_qyt_ore, "coal": s_qyt_coal}
        print(res_by_ship)


    
    if defender["r_regenerationbonus"] is None:
        d_shieldregen = 0
    else:
        d_shieldregen = int(defender["r_regenerationbonus"]) / 200
    if defender["r_repairbonus"] is None:
        d_armorrep = 0
    else:
        d_armorrep = int(defender["r_repairbonus"]) / 200
        
    if attacker["r_regenerationbonus"] is None:
        a_shieldregen = 0
    else:
        a_shieldregen = int(attacker["r_regenerationbonus"]) / 200
    if attacker["r_repairbonus"] is None:
        a_armorrep = 0
    else:
        a_armorrep = int(attacker["r_repairbonus"]) / 200        
    
    if len(attacker_stats) > 0 and attack_mission_type != "siege":
        
        attacker_stats_results = {}
        # print(attacker_stats_results)
        for pos in attacker_stats:
            ship = attacker_stats[pos]
            if ship["position"] not in attacker_stats_results:
                attacker_stats_results[ship["position"]] = ship.copy()
            else:
                attacker_stats_results[ship["position"]]["n"] += ship["n"]
                attacker_stats_results[ship["position"]]["lost"] += ship["lost"]
                attacker_stats_results[ship["position"]]["survivor"] += ship["survivor"]
                attacker_stats_results[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                attacker_stats_results[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                attacker_stats_results[ship["position"]]["shield"] += ship["shield"] * ship["survivor"]   
                attacker_stats_results[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                attacker_stats_results[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                attacker_stats_results[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]
                
        defender_stats_results = {}
        for pos in defender_stats:
            ship = defender_stats[pos]
            if ship["position"] not in defender_stats_results:
                defender_stats_results[ship["position"]] = ship.copy()
            else:
                defender_stats_results[ship["position"]]["n"] += ship["n"]
                defender_stats_results[ship["position"]]["lost"] += ship["lost"]
                defender_stats_results[ship["position"]]["survivor"] += ship["survivor"]
                defender_stats_results[ship["position"]]["structure"] += ship["structure"] * ship["survivor"] 
                defender_stats_results[ship["position"]]["armor"] += ship["armor"] * ship["survivor"] 
                defender_stats_results[ship["position"]]["shield"] += ship["shield"] * ship["survivor"] 
                defender_stats_results[ship["position"]]["laser"] += ship["laser"] * ship["survivor"]
                defender_stats_results[ship["position"]]["bullet"] += ship["bullet"] * ship["survivor"]
                defender_stats_results[ship["position"]]["rocket"] += ship["rocket"] * ship["survivor"]                
        
        table = connection["battleresults"]
        table.upsert({"mission_id": mission_id, "attacker": user, "battle_number": battle_number, "defender": opponent, "date": time_now, "trx_id": trx_id, "result": attacker_result,
                      "initial_attacker_ships": json.dumps(initial_attacker_stats), "final_attacker_ships": json.dumps(attacker_stats_results),
                      "initial_defender_ships": json.dumps(initial_defender_stats), "final_defender_ships": json.dumps(defender_stats_results),
                      "coal": float(new_qty_coal)- q_coal, "ore": float(new_qty_ore) - q_ore, "copper": float(new_qty_copper) - q_copper,
                      "uranium": float(new_qty_uranium) - q_uranium, "attacker_shieldregen": a_shieldregen,
                      "defender_shieldregen": d_shieldregen, "attacker_armorrep": a_armorrep,
                      "defender_armorrep": d_armorrep,
                      "cords_hor_dest": cords_hor_dest, "cords_ver_dest": cords_ver_dest, "cords_hor": cords_hor,
                      "cords_ver": cords_ver}, ["mission_id", "battle_number"])
        
        table = connection["missions"]       
        table.update({"mission_id": mission_id, "qyt_coal": float(new_qty_coal)- q_coal, "qyt_ore": float(new_qty_ore) - q_ore, "qyt_copper": float(new_qty_copper) - q_copper,
                      "qyt_uranium": float(new_qty_uranium) - q_uranium }, ["mission_id"])            
    
    table = connection["activity"]
    table.upsert({"user": user, "mission_id": mission_id, "type": "battle", "date": time_now,  "cords_hor": int(cords_hor_dest),
                  "cords_ver": int(cords_ver_dest), "result": str(attacker_result)}, ["mission_id"])    
    fin_qty_coal = float(new_qty_coal)
    fin_qty_ore = float(new_qty_ore)
    fin_qty_copper = float(new_qty_copper)
    fin_qty_uranium = float(new_qty_uranium)
    # Send ship back after win    
    if attacker_result == 2:
        for ship in ship_list:
            if ship["id"] in attacker_ship_delete and ship["id"] not in attacker_ship_downgrade:
                continue    
            # Calculate resources to load on the ship
            ship_uranium_after_consumption = float(ship["qyt_uranium"]) - consumption_ship[ship["id"]]
            if ship_uranium_after_consumption < 0:
                print("Not enough uranium to fly back. Use the invisible reserve tank.")
                ship_uranium_after_consumption = 0
            # Ship quantity without stealing
            if attack_mission_type != "siege":
                qyt_uranium_ship = ship_uranium_after_consumption + res_by_ship[ship["id"]]["uranium"]
                qyt_coal_ship = ship["qyt_coal"] + res_by_ship[ship["id"]]["coal"]
                qyt_ore_ship = ship["qyt_ore"] + res_by_ship[ship["id"]]["ore"]
                qyt_copper_ship = ship["qyt_copper"] + res_by_ship[ship["id"]]["copper"]
                # Ship quantity after stealing
                fin_qty_coal -= res_by_ship[ship["id"]]["coal"]
                fin_qty_ore -= res_by_ship[ship["id"]]["ore"]
                fin_qty_copper -= res_by_ship[ship["id"]]["copper"]
                fin_qty_uranium -= res_by_ship[ship["id"]]["uranium"]
            else: # don't steel on break siege
                qyt_uranium_ship = ship_uranium_after_consumption
                qyt_coal_ship = ship["qyt_coal"] 
                qyt_ore_ship = ship["qyt_ore"]
                qyt_copper_ship = ship["qyt_copper"]
            # Update ships
            table = connection['ships']
            table.update({"id": str(ship["id"]), "qyt_coal": qyt_coal_ship, "qyt_ore": qyt_ore_ship, "qyt_copper": qyt_copper_ship,
                            "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                            "qyt_uranium": qyt_uranium_ship, "mission_busy_until": t_arrival},['id'])
        # Add virtual ops to send ships back            
        table = connection["virtualops"]
        table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": to_planet_id,
                          "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planet_to_owner, "mission_id": mission_id})            
         
    # Special case for lost with yamato tier => fly back the downgraded yamato
    elif attacker_result == 1:
        if attacker_ship_downgrade:
            for ship in ship_list:
                if ship["id"] in attacker_ship_delete and ship["id"] not in attacker_ship_downgrade:
                    continue        
                qyt_uranium_ship = float(ship["qyt_uranium"]) - consumption_ship[ship["id"]] 
                if qyt_uranium_ship < 0: 
                    print("Not enough uranium to fly back. Use the invisible reserve tank.")
                    qyt_uranium_ship = 0
                table = connection['ships']
                table.update({"id": str(ship["id"]), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                            "qyt_uranium": qyt_uranium_ship, "mission_busy_until": t_arrival},['id'])
   
            table = connection["virtualops"]
            table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": to_planet_id,
                        "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planet_to_owner, "mission_id": mission_id})
        else:
            print("No downgraded ships found to fly back") 
    # Send back ships after draw
    elif attacker_result == 0:
        for ship in ship_list:
            if ship["id"] in attacker_ship_delete and ship["id"] not in attacker_ship_downgrade:
                continue        
            qyt_uranium_ship = float(ship["qyt_uranium"]) - consumption_ship[ship["id"]] 
            if qyt_uranium_ship < 0: 
                print("Not enough uranium to fly back. Use the invisible reserve tank.")
                qyt_uranium_ship = 0
            table = connection['ships']
            table.update({"id": str(ship["id"]), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                            "qyt_uranium": qyt_uranium_ship, "mission_busy_until": t_arrival},['id'])
     
        table = connection["virtualops"]
        table.insert({"tr_status":0, "tr_type":"offload_deploy_mission", "tr_var1": mission_id, "tr_var2": to_planet_id,
                        "date": time_now, "parent_trx": trx_id, "trigger_date": t_arrival, "user":planet_to_owner, "mission_id": mission_id})            

    # Get current season            
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None or last_season["end_date"] < datetime.utcnow():
        current_season = None
    else:
        current_season = last_season
    if current_season is not None:
        season_id = int(current_season["id"])
        leach_rate = current_season["leach_rate"]
        if leach_rate is not None:
            leach_rate = float(leach_rate)
        else:
            leach_rate = 0
    else:
        season_id = None
        leach_rate = None

    table = connection["ranking"]
    user_ranking = table.find_one(user=user)
    destroyed_ships_uranium = user_ranking["destroyed_ships_uranium"]
    n_ships = user_ranking["destroyed_ships"]
    table = connection["ships"]
    for shipid in defender_ship_delete:
        ship = table.find_one(id=shipid)
        if ship is None:
            continue
        if ship["type"][-1] == "1" or ship["type"][-1] == "2":
            build_costs = upgrade_costs[ship["type"][:-1]]['1']
        else:
            build_costs = upgrade_costs[ship["type"]]['1']
        UE = build_costs["coal"] / 8 + build_costs["ore"] / 4 + build_costs["copper"] / 2 + build_costs["uranium"]
        destroyed_ships_uranium += UE
        n_ships += 1
        # Adjust season Reward Points
        if shipid in defender_ship_downgrade:
                          
            # Calculate tier
            defender_user = ship["user"]
            shiptype = ship["type"]
            if shiptype[6:] is not None and shiptype[6:] != "":
                tier = int(shiptype[6:])
            else:
                tier = 0
            oldtier = "yamato"+str(tier)  
            if tier == 1:
                newtier ="yamato"
            else:  
                newtier = "yamato"+str(tier-1)
            if season_id is not None:         
                build_costs = upgrade_costs[oldtier]['1']      
                reward_point = int(build_costs["stardust"])
                # Defender losing points
                table_ranking = connection['seasonranking']
                ranking = table_ranking.find_one(season_id=season_id,user=defender_user)
                if ranking is not None:
                    old_build_reward = int(ranking["build_reward"])
                    old_total_reward = int(ranking["total_reward"])
                else:
                    old_build_reward = 0
                    old_total_reward = 0
                if reward_point != 0:
                    new_build_reward = old_build_reward - reward_point
                    new_total_reward = old_total_reward - reward_point                
                    table_ranking.upsert({"season_id": season_id, "user": defender_user, "last_update": time_now, "build_reward":new_build_reward, "total_reward": new_total_reward}, ["season_id", "user"])
                # Attacker winning points
                table_ranking = connection['seasonranking']
                ranking = table_ranking.find_one(season_id=season_id,user=user)
                if ranking is not None:
                    old_destroy_reward = int(ranking["destroy_reward"])
                    old_total_reward = int(ranking["total_reward"])
                else:
                    old_destroy_reward = 0
                    old_total_reward = 0
                if reward_point != 0 and leach_rate != 0:
                    new_destroy_reward = old_destroy_reward + reward_point * leach_rate
                    new_total_reward = old_total_reward + reward_point * leach_rate                
                    table_ranking.upsert({"season_id": season_id, "user": user, "last_update": time_now, "destroy_reward":new_destroy_reward, "total_reward": new_total_reward}, ["season_id", "user"])
            # Cancel Yamato market orders
            table = connection["asks"]
            ask = table.find_one(uid=shipid, cancel_trx=None, buy_trx=None, sold=None, failed=None)
            if ask is not None:
                if ask["id"] is not None:
                    table.update({"id": ask["id"], "cancel_trx": trx_id , "failed": time_now}, ["id"])
            # Downgrade destroyed Yamato
            table = connection["ships"]
            table.update({"id": str(shipid), "type": newtier},['id'])

    table = connection["ranking"]
    data = {"user": user, "destroyed_ships": n_ships, "destroyed_ships_uranium":destroyed_ships_uranium}
    table.upsert(data, ["user"])
    
    for opponent in attacker_ship_delete_by_opponent:
        
        table = connection["ranking"]
        opponent_ranking = table.find_one(user=opponent)
        destroyed_ships_uranium = opponent_ranking["destroyed_ships_uranium"]
        n_ships = opponent_ranking["destroyed_ships"]    
        table = connection["ships"]
        for shipid in attacker_ship_delete_by_opponent[opponent]:
            ship = table.find_one(id=shipid)
            if ship is None:
                continue
            if ship["type"][-1] == "1" or ship["type"][-1] == "2":
                build_costs = upgrade_costs[ship["type"][:-1]]['1']
            else:
                build_costs = upgrade_costs[ship["type"]]['1']
            UE = build_costs["coal"] / 8 + build_costs["ore"] / 4 + build_costs["copper"] / 2 + build_costs["uranium"]
            destroyed_ships_uranium += UE 
            n_ships += 1
            # Adjust season Reward Points
            if shipid in attacker_ship_downgrade:           
                # Calculate tier
                shiptype = ship["type"]
                if shiptype[6:] is not None and shiptype[6:] != "":
                    tier = int(shiptype[6:])
                else:
                    tier = 0
                oldtier = "yamato"+str(tier)  
                if tier == 1:
                    newtier ="yamato"
                else:  
                    newtier = "yamato"+str(tier-1)  
                if season_id is not None:          
                    build_costs = upgrade_costs[oldtier]['1']    
                    reward_point = int(build_costs["stardust"])
                    # Attacker losing points
                    table_ranking = connection['seasonranking']
                    ranking = table_ranking.find_one(season_id=season_id,user=user)
                    if ranking is not None:
                        old_build_reward = int(ranking["build_reward"])
                        old_total_reward = int(ranking["total_reward"])
                    else:
                        old_build_reward = 0
                        old_total_reward = 0
                    if reward_point != 0:
                        new_build_reward = old_build_reward - reward_point
                        new_total_reward = old_total_reward - reward_point                
                        table_ranking.upsert({"season_id": season_id, "user": user, "last_update": time_now, "build_reward":new_build_reward, "total_reward": new_total_reward}, ["season_id", "user"])
                    # Opponent winning points
                    table_ranking = connection['seasonranking']
                    ranking = table_ranking.find_one(season_id=season_id,user=opponent)
                    if ranking is not None:
                        old_destroy_reward = ranking["destroy_reward"]
                        old_total_reward = ranking["total_reward"]
                    else:
                        old_destroy_reward = 0
                        old_total_reward = 0
                    if reward_point != 0 and leach_rate != 0:
                        new_destroy_reward = old_destroy_reward + reward_point * leach_rate
                        new_total_reward = old_total_reward + reward_point *  leach_rate                
                        table_ranking.upsert({"season_id": season_id, "user": opponent, "last_update": time_now, "destroy_reward":new_destroy_reward, "total_reward": new_total_reward}, ["season_id", "user"])
                # Cancel Yamato market orders
                table = connection["asks"]
                ask = table.find_one(uid=shipid, cancel_trx=None, buy_trx=None, sold=None, failed=None)
                if ask is not None:
                    if ask["id"] is not None:
                        table.update({"id": ask["id"], "cancel_trx": trx_id , "failed": time_now}, ["id"])
                # Downgrade destroyed Yamato
                table = connection["ships"]
                if shipid is not None:
                    table.update({"id": str(shipid), "type": newtier},['id'])

        table = connection["ranking"]
        data = {"user": opponent, "destroyed_ships": n_ships, "destroyed_ships_uranium":destroyed_ships_uranium}
        table.upsert(data, ["user"])        
    
    table = connection["ships"]
    for shipid in attacker_ship_delete + defender_ship_delete:
        if shipid in attacker_ship_downgrade + defender_ship_downgrade:
            continue  
        else:
            # Fail Market Orders           
            table = connection["asks"]
            ask = table.find_one(uid=shipid, cancel_trx=None, buy_trx=None, sold=None, failed=None)
            if ask is not None:
                if ask["id"] is not None:
                    table.update({"id": ask["id"], "cancel_trx": trx_id , "failed": time_now}, ["id"])
            # Delete Ship
            table = connection["ships"]
            if shipid is not None:
                table.delete(id=shipid)
    
    table = connection["missions"]
    for support_mission_id in defence_mission_ids:
        mission_data = table.find_one(mission_id=support_mission_id)
        if mission_data is None:
            continue
        if "mission_type" in mission_data and mission_data["mission_type"] != "support" and mission_data["mission_type"] != "siege" and mission_data["mission_type"] != "upgradeyamato" :
            continue
        table = connection["ships"]
        n = table.count(user=mission_data["user"], mission_id=support_mission_id, cords_hor=cords_hor_dest, cords_ver=cords_ver_dest)
        if n == 0:
            table = connection["missions"]
            if "mission_type" in mission_data and mission_data["mission_type"] == "siege":
                table.update({"mission_id": support_mission_id, "busy_until_return":  time_now}, ["mission_id"])
            else:
                table.update({"mission_id": support_mission_id, "cancel_trx": trx_id, "busy_until_return":  None}, ["mission_id"])
            table = connection["activity"]
            table.upsert({"user": mission_data["user"], "mission_id": support_mission_id, "type": "battle",
                          "date": time_now,  "cords_hor": int(cords_hor_dest),
                          "cords_ver": int(cords_ver_dest), "result": "1"}, ["mission_id"])
        if n == 1 and len(defender_ship_downgrade) == 1 and "mission_type" in mission_data and mission_data["mission_type"] == "upgradeyamato":
            table = connection["missions"]
            table.update({"mission_id": support_mission_id, "busy_until_return":  time_now}, ["mission_id"])
            table = connection["activity"]
            table.upsert({"user": mission_data["user"], "mission_id": support_mission_id, "type": "battle",
                        "date": time_now,  "cords_hor": int(cords_hor_dest),
                        "cords_ver": int(cords_ver_dest), "result": "1"}, ["mission_id"])                                                   
                
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])    

    
    return (True)
    
# VOPS "offload_return"
def offload_return (shipid, to_planet_id, mission_id, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    # increase the level of resources on the target planet
    connection = connectdb()
    print("offload")
    
    (s_type,s_level,s_user,s_cords_hor,s_cords_ver,s_qty_copper,s_qty_uranium,s_qty_coal,s_qty_ore,s_busy_until,tmp_mission_id, home_planet_id) = get_shipdata(shipid)

    planet_id = get_planetid (s_cords_hor,s_cords_ver)
    if planet_id is None:
        print("No planet at offload location")
        return False
    print(planet_id)
    table = connection["planets"]    
    planet_to_data = table.find_one(id=to_planet_id)
    if planet_to_data is None:
        print("No planet with id %s" % str(to_planet_id))
        return False        
    table = connection['ships']
    shipdata = table.find_one(id=shipid)

    distance = get_distance(s_cords_hor,s_cords_ver,planet_to_data['cords_hor'],planet_to_data['cords_ver'])

    apply_battlespeed = False
    if shipdata["user"] is not None and time_now is not None:
        table = connection["users"]  
        userdata = table.find_one(username=shipdata["user"])
        battle_speed_buff = userdata["b_battlespeed"]
        if battle_speed_buff is not None:
            if battle_speed_buff > time_now:
                apply_battlespeed = True  

    # calculate the arrival time of the ships    
    (consumption, flight_duration) = get_flight_param(shipstats[s_type],distance,apply_battlespeed)        
    t_arrival = time_now + timedelta(flight_duration / 24)
    
    # check if there is enough resources on the starting planet - if not return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planet_id, parameter, time_now)
    
    fin_qty_coal = float(new_qty_coal) + float(s_qty_coal)
    fin_qty_ore = float(new_qty_ore) + float(s_qty_ore)
    fin_qty_copper = float(new_qty_copper) + float(s_qty_copper)
    new_ship_qty_uranium = float(s_qty_uranium) - consumption
    if new_ship_qty_uranium > 0:
        fin_qty_uranium = float(new_qty_uranium) + new_ship_qty_uranium
    else:
        print("Not enough uranium to fly back. Use the invisible reserve tank.")
        fin_qty_uranium = float(new_qty_uranium) 
       
    table = connection['ships']
    table.update({"id": str(shipid), "cords_hor": int(planet_to_data['cords_hor']), "cords_ver": int(planet_to_data['cords_ver']),
                    "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                    "qyt_uranium": 0, "mission_busy_until": t_arrival},['id'])    
    
    table = connection['planets']
    data = dict(id=planet_id,qyt_ore=fin_qty_ore,qyt_coal=fin_qty_coal,qyt_copper=fin_qty_copper,qyt_uranium=fin_qty_uranium,last_update=time_now)
    table.update(data,['id'])    

    
    return (True)


def update_ranking_user(username, time_now):
    connection = connectdb()
    meta_skill = 0
    rate_coal = 0
    rate_ore = 0
    rate_copper = 0
    rate_uranium = 0
    n_planets = 0
    n_explorartion = 0
    table = connection["users"]
    user = table.find_one(username=username)
    if user is None:
        return
    for key in user:
        if key[:2] == "r_" and key[-4:] != "busy":
            skill = user[key]
            if skill is None:
                skill = 0
            meta_skill += int(skill)
    table=connection["planets"]
    for planetdata in table.find(user=user["username"]):
        n_planets += 1
        rate_coal += planetdata["rate_coal"]
        rate_ore += planetdata["rate_ore"]
        rate_copper += planetdata["rate_copper"]
        rate_uranium += planetdata["rate_uranium"]
    table = connection["space"]
    n_explorartion = table.count(user=user["username"])
    table = connection["ships"]
    n_ships = table.count(user=user["username"])
    
    meta_rate = rate_coal / 80 + rate_ore / 40 + rate_copper / 20 + rate_uranium / 10
    table = connection["ranking"]
    data = {"user": user["username"], "last_update": time_now, "rate_coal": rate_coal,
                      "rate_ore": rate_ore, "rate_copper": rate_copper, "rate_uranium": rate_uranium,
                      "meta_skill": meta_skill, "explorations": n_explorartion, "planets": n_planets,
                      "meta_rate": meta_rate, "ships": n_ships}
    table.upsert(data, ["user"])
        

def update_ranking(parameter, time_now):
    connection = connectdb()
        
    table = connection["ranking"]
    oldest_entry = table.find_one(order_by="last_update")
    if oldest_entry is None or oldest_entry["last_update"] is None:
        return
    age = (time_now- oldest_entry["last_update"]).total_seconds() / 60 / 60
    limit = int(age)
    if limit >  100:
        limit = int(100)
    if limit <= 0:
        return
    print("Update %d entries - %s - age %.2f h" % (limit, str(oldest_entry["last_update"]), age))
    for data in table.find(order_by="last_update", _limit=limit):
        update_ranking_user(data["user"], time_now)

def update_resource_rate(planetid, parameter, time_now):
    production_rates = parameter["production_rates"]
    planet_rarity = parameter["planet_rarity"]

    ore_bonus_percentage = 0
    coal_bonus_percentage = 0
    copper_bonus_percentage = 0
    uranium_bonus_percentage = 0

    # get the planet data from the database
    connection = connectdb()
    table=connection["planets"]
    planetdata = table.find_one(id=planetid)    
    
    if planetdata is None:
        print("Could not find planetid %s" % str(planetid))
        return      
         
    # get the current level of available resources from the database
    planettype = planetdata['planet_type']
    if time_now < datetime(2019, 5, 11, 13, 34, 0):
        if planetid in ['P-ZU1JXAEU4KW', 'P-ZCQ6XF6HTSW', 'P-ZHYWH6QELGG', 'P-ZLSPVTUM2CW', 'P-Z6SI0OXFI40', 'P-Z1DYC1A3D00', 'P-ZWQK5FV1GCW', 'P-Z1EXI322Y0G', 'P-Z7LAB17RAI8', 'P-Z9BGQ3Q6UWG', 'P-ZCVC4FATUR4', 'P-Z38KQGMV7WW']:
            planettype = 2    
    bonus = planetdata['bonus']

    planetowner = planetdata['user']

    level_coal = planetdata['level_coal']
    level_ore = planetdata['level_ore']
    level_copper = planetdata['level_copper']
    level_uranium = planetdata['level_uranium']
    level_research = planetdata['level_research']
    #get the depot rates from the database
    level_coaldepot = planetdata['level_coaldepot']
    level_oredepot = planetdata['level_oredepot']
    level_copperdepot = planetdata['level_copperdepot']
    level_uraniumdepot = planetdata['level_uraniumdepot']
    shieldcharge_busy = planetdata['shieldcharge_busy']
    boost_percentage = planetdata['boost_percentage']
    if boost_percentage is None:
        boost_percentage = 0
    else:
        boost_percentage = float(boost_percentage)
    
    if bonus in planet_rarity:
        raritydata = planet_rarity[bonus]
    else:
        print("planetlevels: Could not find %s" % str(bonus))
        table=connection["planetlevels"]
        raritydata = table.find_one(rarity=bonus)
    p_bonus_percentage = raritydata['p_bonus_percentage']
    if p_bonus_percentage is None:
        p_bonus_percentage = 0

    ore_bonus_percentage = 0
    coal_bonus_percentage = 0
    copper_bonus_percentage = 0
    uranium_bonus_percentage = 0
    if time_now < datetime(2019, 5, 11, 20, 14, 0):
        if int(planettype) == 2:
            ore_bonus_percentage = p_bonus_percentage + boost_percentage
        if int(planettype) == 3:
            coal_bonus_percentage = p_bonus_percentage + boost_percentage
    else:
        if int(planettype) == 3:
            ore_bonus_percentage = p_bonus_percentage + boost_percentage
        if int(planettype) == 2:
            coal_bonus_percentage = p_bonus_percentage + boost_percentage
    if int(planettype) == 4:
        copper_bonus_percentage = p_bonus_percentage + boost_percentage
    if int(planettype) == 5:
        uranium_bonus_percentage = p_bonus_percentage + boost_percentage

    if shieldcharge_busy is not None and shieldcharge_busy > time_now:
        charge_reduction = 0.9
    else:
        charge_reduction = 1
        

    table = connection["users"]
    userdata = table.find_one(username=planetowner)
    # boost level
    orebooster = 0
    coalbooster = 0
    copperbooster = 0
    uraniumbooster = 0
    depotincrease = 0
    if userdata is not None:
        if userdata["r_orebooster"] is not None:
            orebooster = userdata["r_orebooster"]
        if userdata["r_coalbooster"] is not None:
            coalbooster = userdata["r_coalbooster"]
        if userdata["r_copperbooster"] is not None:
            copperbooster = userdata["r_copperbooster"]
        if userdata["r_uraniumbooster"] is not None:
            uraniumbooster = userdata["r_uraniumbooster"]
        if userdata["r_depotincrease"] is not None:
            depotincrease = userdata["r_depotincrease"]
            
    cap_uraniumdepot = production_rates["uraniumdepot"][str(level_uraniumdepot)]["uranium"] * (1 + (depotincrease + level_research) * 2.5 / 100)
    cap_oredepot = production_rates["oredepot"][str(level_oredepot)]["ore"] * (1 + (depotincrease + level_research) * 2.5 / 100)
    cap_coaldepot = production_rates["coaldepot"][str(level_coaldepot)]["coal"] * (1 + (depotincrease + level_research) * 2.5 / 100)
    cap_copperdepot = production_rates["copperdepot"][str(level_copperdepot)]["copper"] * (1 + (depotincrease + level_research) * 2.5 / 100)
    

    boost_percentage_per_level = 0.5
    
    coal_production_rate = production_rates["coalmine"][str(level_coal)]["coal"] * (1 + (boost_percentage_per_level * coalbooster + coal_bonus_percentage) / 100) * charge_reduction
    ore_production_rate = production_rates["oremine"][str(level_ore)]["ore"] * (1 + (boost_percentage_per_level * orebooster +  ore_bonus_percentage) / 100 ) * charge_reduction
    copper_production_rate =production_rates["coppermine"][str(level_copper)]["copper"] * (1 + (boost_percentage_per_level * copperbooster + copper_bonus_percentage) / 100 ) * charge_reduction
    uranium_production_rate = production_rates["uraniummine"][str(level_uranium)]["uranium"] * (1 + (boost_percentage_per_level * uraniumbooster + uranium_bonus_percentage) / 100 ) * charge_reduction
    table=connection["planets"]
    table.update({"id": planetid, "rate_coal":coal_production_rate, "rate_ore": ore_production_rate,
                  "rate_copper": copper_production_rate, "rate_uranium": uranium_production_rate,
                  "depot_coal": cap_coaldepot, "depot_ore": cap_oredepot, "depot_copper": cap_copperdepot,
                  "depot_uranium": cap_uraniumdepot}, ["id"])



def get_resource_levels(planetid, parameter, time_now):
    production_rates = parameter["production_rates"]     

    # get the planet data from the database
    # Connect to the database
    connection = connectdb()
    table=connection["planets"]
    planetdata = table.find_one(id=planetid)    
    
    if planetdata is None:
        print("Could not find planetid %s" % str(planetid))
        return False    
         
    # get the current level of available resources from the database
    qty_coal = planetdata['qyt_coal']
    qty_ore = planetdata['qyt_ore']
    qty_copper = planetdata['qyt_copper']
    qty_uranium = planetdata['qyt_uranium']
    level_base = planetdata['level_base']
    level_research = planetdata['level_research']
    level_shipyard = planetdata['level_shipyard']
    # Rates are per hour
    rate_coal = planetdata["rate_coal"]
    rate_ore = planetdata["rate_ore"]
    rate_copper = planetdata["rate_copper"]
    rate_uranium = planetdata["rate_uranium"]
    if rate_coal == 0 or rate_ore == 0 or rate_copper == 0 or rate_uranium == 0:
        update_resource_rate(planetid, parameter, time_now)
        table=connection["planets"]
        planetdata = table.find_one(id=planetid)        
        rate_coal = planetdata["rate_coal"]
        rate_ore = planetdata["rate_ore"]
        rate_copper = planetdata["rate_copper"]
        rate_uranium = planetdata["rate_uranium"]
    
    cap_coaldepot = planetdata["depot_coal"]
    cap_oredepot = planetdata["depot_ore"]
    cap_copperdepot = planetdata["depot_copper"]
    cap_uraniumdepot = planetdata["depot_uranium"]    
    if cap_coaldepot == 0 or cap_oredepot == 0 or cap_copperdepot == 0 or cap_uraniumdepot == 0:
        update_resource_rate(planetid, parameter, time_now)
        table=connection["planets"]
        planetdata = table.find_one(id=planetid)        
        cap_coaldepot = planetdata["depot_coal"]
        cap_oredepot = planetdata["depot_ore"]
        cap_copperdepot = planetdata["depot_copper"]
        cap_uraniumdepot = planetdata["depot_uranium"]  
        
    # calculate the up-to-date level
    if planetdata['last_update'] is None:
        last_update = time_now
    else:
        last_update = planetdata['last_update']

    time_since_update = (time_now - last_update).total_seconds()

    new_qty_coal = min((float(qty_coal) +float(rate_coal)/(60*60*24)*float(time_since_update)),cap_coaldepot)
    new_qty_ore = min((float(qty_ore) +float(rate_ore)/(60*60*24)*float(time_since_update)),cap_oredepot)
    new_qty_copper =min(( float(qty_copper) +float(rate_copper)/(60*60*24)*float(time_since_update)),cap_copperdepot)
    new_qty_uranium = min((float(qty_uranium) +float(rate_uranium)/(60*60*24)*float(time_since_update)), cap_uraniumdepot)

    if new_qty_coal < qty_coal:
        new_qty_coal = qty_coal
    if new_qty_ore < qty_ore:
        new_qty_ore = qty_ore
    if new_qty_copper < qty_copper:
        new_qty_copper = qty_copper
    if new_qty_uranium < qty_uranium:
        new_qty_uranium = qty_uranium
    
    return (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard)


def build_ship(planetid,ship, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    upgrade_costs = parameter["upgrade_costs"]
    blueprint_ships = ["battlecruiser1","battlecruiser2","carrier1","carrier2","corvette1","corvette2","cruiser1","cruiser2",
                       "destroyer1","destroyer2","dreadnought1","dreadnought2", "explorership1", "explorership2","frigate1",
                       "frigate2", "transportship1", "transportship2", "scout1", "scout2", "patrol1", "patrol2", "cutter1", "cutter2","yamato", "yamato1", "yamato2", "yamato3","yamato4","yamato5","yamato6","yamato7","yamato8","yamato9","yamato10","yamato11","yamato12",
                      "yamato13","yamato14","yamato15","yamato16","yamato17","yamato18","yamato19","yamato20"]    
    # get the planet data from the database
    connection = connectdb()
    table = connection["planets"]
    planetdata = table.find_one(id=planetid)

    if planetdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)                
    if time_now > datetime(2019, 7, 1, 12, 15, 0):
        
        if ship in blueprint_ships:
            if planetdata['blueprints'] is None:
                print ("You do not own this blueprint: %s" % str(ship)) 
                return (False)
    
            elif planetdata['blueprints'] is not None and ship not in planetdata['blueprints']:
                print ("You do not own this blueprint: %s" % str(ship)) 
                return (False)

    cords_hor = planetdata['cords_hor']
    cords_ver = planetdata['cords_ver']
    planetowner = planetdata['user']
    table = connection["users"]
    userdata = table.find_one(username=planetowner)    
    new_building_level = '1'
  
    if ship not in shipstats:
        print("Error, %s is not a known ship type!" % ship)
        return False
    shipyard_level_requirement =  int(shipstats[ship]["shipyard_level"])
    if ship in upgrade_costs and time_now > datetime(2019, 7, 4, 21, 20,0):
        build_costs = upgrade_costs[ship][new_building_level]
    elif ship[-1] == "1" or ship[-1] == "2":
        build_costs = upgrade_costs[ship[:-1]][new_building_level]
    else:
        print("Error, %s has no upgrade costs!" % ship)
        return False
    
    if time_now < datetime(2019, 5, 3, 8, 56, 4) and ship == "corvette":
        build_costs["coal"] = 1736
        build_costs["ore"] = 2430 
        build_costs["copper"] = 1042
        build_costs["uranium"] = 347
        build_costs["upgrade_time"] = 38278

    coal_costs = build_costs['coal']
    ore_costs = build_costs['ore']
    copper_costs = build_costs['copper']
    uranium_costs = build_costs['uranium']

    # get the current level of available resources from the database
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)

    if level_shipyard < shipyard_level_requirement:
        print("Shipyard must be %d" % shipyard_level_requirement)
        return False        
        
    skill_requirement = 20
    if ship == "transportship" or ship == "Transporter"  or ship.lower()[:-1] == "transportship":
        if userdata["r_Transporter"] is None or userdata["r_Transporter"] < skill_requirement:
            print("Transporter skill must be %d" % skill_requirement)
            return False
    elif ship == "explorership" or ship == "Explorer"  or ship.lower()[:-1] == "explorership":
        if userdata["r_Explorer"] is None or userdata["r_Explorer"] < skill_requirement:
            print("Explorer skill must be %d" % skill_requirement)
            return False
    elif ship.lower() == "corvette" or ship.lower()[:-1] == "corvette":
        if userdata["r_Corvette"] is None or userdata["r_Corvette"] < skill_requirement:
            print("Corvette skill must be %d" % skill_requirement)
            return False
    elif ship.lower() == "frigate" or ship.lower()[:-1] == "frigate":
        if userdata["r_Frigate"] is None or userdata["r_Frigate"] < skill_requirement:
            print("Frigate skill must be %d" % skill_requirement)
            return False   
    elif ship.lower() == "destroyer" or ship.lower()[:-1] == "destroyer":
        if userdata["r_Destroyer"] is None or userdata["r_Destroyer"] < skill_requirement:
            print("Destroyer skill must be %d" % skill_requirement)
            return False   
    elif ship.lower() == "cruiser" or ship.lower()[:-1] == "cruiser" :
        if userdata["r_Cruiser"] is None or userdata["r_Cruiser"] < skill_requirement:
            print("Cruiser skill must be %d" % skill_requirement)
            return False   
    elif ship.lower() == "battlecruiser" or ship.lower()[:-1] == "battlecruiser":
        if userdata["r_Battlecruiser"] is None or userdata["r_Battlecruiser"] < skill_requirement:
            print("Battlecruiser skill must be %d" % skill_requirement)
            return False 
    elif ship.lower() == "carrier" or ship.lower()[:-1] == "carrier":
        if userdata["r_Carrier"] is None or userdata["r_Carrier"] < skill_requirement:
            print("Carrier  skill must be %d" % skill_requirement)
            return False 
    elif ship.lower() == "dreadnought" or ship.lower()[:-1] == "dreadnought":
        if userdata["r_Dreadnought"] is None or userdata["r_Dreadnought"] < skill_requirement:
            print("Dreadnought  skill must be %d" % skill_requirement)
            return False
    elif ship.lower() == "scout" or ship.lower()[:-1] == "scout":
        if userdata["r_Scout"] is None or userdata["r_Scout"] < skill_requirement:
            print("Scout  skill must be %d" % skill_requirement)
            return False
    elif ship.lower() == "patrol" or ship.lower()[:-1] == "patrol":
        if userdata["r_Patrol"] is None or userdata["r_Patrol"] < skill_requirement:
            print("Patrol  skill must be %d" % skill_requirement)
            return False
    elif ship.lower() == "cutter" or ship.lower()[:-1] == "cutter":
        if userdata["r_Cutter"] is None or userdata["r_Cutter"] < skill_requirement:
            print("Cutter  skill must be %d" % skill_requirement)
            return False 
    elif ship.lower() == "yamato" or ship.lower()[:-1] == "yamato":
        if userdata["r_Yamato"] is None or userdata["r_Yamato"] < skill_requirement:
            print("Yamato  skill must be %d" % skill_requirement)
            return False 
        
    table = connection["ships"]
    last_build_ship = table.find_one(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver, type=ship, order_by="-busy_until")
    if last_build_ship is not None:
        if last_build_ship["busy_until"] > time_now:
            print("ship building not finished")
            return False
        
    build_time = timedelta(float(build_costs['upgrade_time'])/(60*60*24) * (1 - 0.01 * level_shipyard))
    busy_until = time_now + build_time
    # check if the necessary resouces are available
    if (new_qty_coal>=coal_costs and new_qty_ore>=ore_costs and new_qty_copper>=copper_costs and new_qty_uranium>= uranium_costs):
        final_qty_coal = new_qty_coal - coal_costs
        final_qty_ore = new_qty_ore - ore_costs
        final_qty_copper = new_qty_copper - copper_costs
        final_qty_uranium = new_qty_uranium - uranium_costs
    else:
        print ("Lacking resources")
        if new_qty_coal>=coal_costs:
            print ("Enough coal")
        if new_qty_ore>=ore_costs:
            print ("Enough ore")
        if new_qty_copper>=copper_costs:
            print ("Enough copper")
        if new_qty_uranium>=uranium_costs:
            print ("Enough uranium")

        return False
    seed = get_seed(block_num, trx_id) 
    set_seed(seed)
    uid_prefix = "S-"
    uid = uid_from_seed(uid_prefix)    

    # Update the database with the new data
    table = connection["ships"]
    table.insert({"id":uid, "type": ship, "level": 1, "user": planetowner, "cords_hor": cords_hor, "cords_ver": cords_ver,
                  "qyt_copper": 0, "qyt_uranium": 0, "qyt_ore": 0, "qyt_coal": 0, "busy_until": (busy_until),"last_update": (time_now),
                  "block_num": block_num, "trx_id": trx_id, "created": time_now})

    table = connection["planets"]
    table.update({"id": planetid, "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper,
                  "qyt_uranium": final_qty_uranium, "last_update": (time_now)}, ["id"])

    return True

def finish_skill(user, skill, newlevel, parameter, time_now, block_num, trx_id):
    skill_costs = parameter["skill_costs"]
    if skill not in skill_costs:
        print("%s is not in skillcosts table" % skill)
        return False
    connection = connectdb()
    # check the research levels
    table = connection['users']
    userdata = table.find_one(username=user)
    if userdata is None:
        print("Could not find user %s" % user)
        return False    
    level_parameter = "r_%s" % skill
    research_skill_level = (userdata[level_parameter])
    if research_skill_level is None:
        research_skill_level = 0
    if int(newlevel) != research_skill_level + 1:
        print("newlevel does not fit ")
        return False
    if str(newlevel) not in skill_costs[skill]:
        print("Enhance %s is not possible, as %s does not exists in skill costs" % (skill, str(newlevel)))
        return False
    
    table = connection["planets"]
    planetid_list = []
    for p in table.find(user=user):
        planetid_list.append(p["id"])
        planetid = p["id"]
        (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
        table = connection["planets"]
        table.update({"id": planetid, "qyt_coal": new_qty_coal, "qyt_ore": new_qty_ore, "qyt_copper": new_qty_copper,
                      "qyt_uranium": new_qty_uranium, "last_update": (time_now)}, ["id"])

    table = connection['users']
    table.update({str(level_parameter): int(newlevel), "username": user}, ["username"])

    for planetid in planetid_list:
        update_resource_rate(planetid, parameter, time_now)
    return True          
    
def enhance(user, planetid, skill, parameter, time_now, trx_id, transaction_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    
    if skill not in skill_costs:
        print("%s is not in skillcosts table" % skill)
        return False
    
    if skill in ["bunker", "enlargebunker"] and time_now < datetime(2019, 5, 10, 8, 0, 0):
        print("Skill %s does not exists in the game right now." % skill)
        return False     
    
    connection = connectdb()
    # check the research levels
    table = connection['users']
    userdata = table.find_one(username=user)
    if userdata is None:
        print("Could not find user %s" % user)
        return False
    
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)            
    
    busy_parameter = "r_%s_busy" % skill
    level_parameter = "r_%s" % skill
    
    research_skill_level = (userdata["r_researchcenter"])
    if research_skill_level is None:
        research_skill_level = 0
    skilllevel = userdata[level_parameter]
    if skilllevel is None:
        skilllevel = 0
    new_skill_level = int(int(skilllevel) +1)
    if str(new_skill_level) not in skill_costs[skill]:
        print("Enhance %s is not possible, as %s does not exists in skill costs" % (skill, str(new_skill_level)))
        return False    
    # get the current ressource levels
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
    if skill_costs[skill][str(new_skill_level)]['ore'] > new_qty_ore:
        print("Not enough ore")
        return (False)
    if skill_costs[skill][str(new_skill_level)]['coal'] > new_qty_coal:
        print("Not enough coal")
        return (False)
    if skill_costs[skill][str(new_skill_level)]['copper'] > new_qty_copper:
        print("Not enough copper")
        return (False)
    if skill_costs[skill][str(new_skill_level)]['uranium'] > new_qty_uranium:
        print("Not enough uranium")
        return (False)
    
    # calculate the new resource level
    final_p_qty_ore = float(new_qty_ore) - float(skill_costs[skill][str(new_skill_level)]['ore'])
    final_p_qty_coal = float(new_qty_coal) - float(skill_costs[skill][str(new_skill_level)]['coal'])
    final_p_qty_copper = float(new_qty_copper) - float(skill_costs[skill][str(new_skill_level)]['copper'])
    final_p_qty_uranium = float(new_qty_uranium) - float(skill_costs[skill][str(new_skill_level)]['uranium']) 
    
    try:
        if userdata[busy_parameter] is None:
            busy_time = datetime(1990,1,1,1,1,1,1)
        else:
            busy_time  = userdata[busy_parameter]
    except:
        busy_time = datetime(1990,1,1,1,1,1,1)
    if time_now < busy_time:
        print("cannot upgrade this skill. It is currently busy, %.2f min to go" % ((time_now - busy_time).total_seconds() / 60))
        return(False)
    upgrade_time = timedelta(float(skill_costs[skill][str(new_skill_level)]['research_time'])/(60*60*24))
    
    busy_until = time_now + upgrade_time
    print ("Charging will take until: "+str(busy_until))
    connection.begin()
    try:
        table = connection['planets']
        table.update({"qyt_coal": final_p_qty_coal, "qyt_ore": final_p_qty_ore, "qyt_copper": final_p_qty_copper,
                      "qyt_uranium": final_p_qty_uranium, "last_update": (time_now), "id": planetid}, ["id"])
        table = connection['users']
        table.update({str(busy_parameter): (busy_until), "username": user}, ["username"])
        table = connection["virtualops"]    
        table.insert({"tr_status":0, "tr_type":"finishskill", "tr_var1": user, "tr_var2": skill, "tr_var3":str(new_skill_level),
                      "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until, "user":user})    
        table = connection["transactions"]
        table.update({"id": transaction_id, "tr_status": 1}, ["id"])  
        connection.commit()
    except:
        connection.rollback() 
        print ("Database transaction failed")
        return False
    return True

def finish_building(planetid, building, newlevel, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]    
    # get the planet data from the database
    connection = connectdb()
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)
    #Check which level is the building that should be updated
    (building_level, busy_parameter, skill_name) = get_building_parameter(building)
    if building_level is None:
        print("Unkown building %s" % building)
        return False
    buildinglevel = pdata[building_level]
    if buildinglevel is None:
        buildinglevel = 0
    if int(newlevel) != buildinglevel + 1:
        print("newlevel does not fit ")
        return False
    if str(newlevel) not in upgrade_costs[building]:
        print("Upgrade %s is not possible, as %s does not exists in upgrade costs" % (building, str(newlevel)))
        return False
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
    
    table = connection["planets"]
    table.update({"id": planetid, str(building_level): int(newlevel), "qyt_coal": new_qty_coal, "qyt_ore": new_qty_ore, "qyt_copper": new_qty_copper,
                  "qyt_uranium": new_qty_uranium, "last_update": (time_now)}, ["id"])    

    update_resource_rate(planetid, parameter, time_now)

    return True      

def finish_charging(planetid, building, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]    
    connection = connectdb()
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)

    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
    
    table = connection["planets"]
    table.update({"id": planetid, "qyt_coal": new_qty_coal, "qyt_ore": new_qty_ore, "qyt_copper": new_qty_copper,
                  "qyt_uranium": new_qty_uranium, "shieldcharged": True, "last_update": (time_now)}, ["id"])    

    update_resource_rate(planetid, parameter, time_now)

    return True      

def charge(planetid,building, parameter, time_now, trx_id, transaction_id):
    print("charge shildgenerator")
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    # get the planet data from the database
    if building != "shieldgenerator":
        return False
    
    connection = connectdb()
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)          
    planetowner = pdata["user"]
    
    table = connection['users']
    userdata = table.find_one(username=planetowner)
    if userdata is None:
        print("Could not find user %s" % user)        
        return False    
       
    #Check which level is the building that should be updated
    (building_level, busy_parameter, skill_name) = get_building_parameter(building)
    if building_level is None:
        print("Unknown building %s" % building)
        return False

    buildinglevel = pdata[building_level]
    if buildinglevel is None:
        buildinglevel = 0

    # get the current level of available resources from the database
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
    final_qty_coal = new_qty_coal
    final_qty_ore = new_qty_ore
    final_qty_copper = new_qty_copper
    final_qty_uranium = new_qty_uranium
    busy_time = pdata["shieldcharge_busy"]
    if busy_time is None:
        busy_time = datetime(1990,1,1,1,1,1,1)
    if time_now < busy_time:
        print("cannot charge this building. It is currently charging, %.2f min to go" % ((time_now - busy_time).total_seconds() / 60))
        return(False)
    if pdata["shieldcharged"]:
        print("Already charged..")     
        return False
    # get the new time until the building will be busy:
    charge_time = timedelta(float(buildinglevel * 4.8)/(24))
    busy_until = time_now + charge_time
    print ("charging will take until: "+str(busy_until))
       
    table = connection["planets"]
    table.update({"id": planetid, "shieldcharge_busy": (busy_until),
                          "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper,
                          "qyt_uranium": final_qty_uranium, "last_update": (time_now)}, ["id"])    
    update_resource_rate(planetid, parameter, time_now)
    
    table = connection["virtualops"]    
    table.insert({"tr_status":0, "tr_type":"finishcharging", "tr_var1": planetid, "tr_var2": building,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until, "user":planetowner})
    table = connection["transactions"]
    table.update({"id": transaction_id, "tr_status": 1}, ["id"])  

    return True

def enable(planetid,building, parameter, time_now, trx_id, transaction_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    # get the planet data from the database
    if building != "shieldgenerator":
        return False
    
    connection = connectdb()
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)          
    planetowner = pdata["user"]
    
    table = connection['users']
    userdata = table.find_one(username=planetowner)
    if userdata is None:
        print("Could not find user %s" % user)  
        return False    
       
    #Check which level is the building that should be updated
    (building_level, busy_parameter, skill_name) = get_building_parameter(building)
    if building_level is None:
        print("Unkown building %s" % building)
        return False

    buildinglevel = pdata[building_level]
    if buildinglevel is None:
        buildinglevel = 0

    shieldprotection_busy = pdata["shieldprotection_busy"]
    if shieldprotection_busy is None:
        shieldprotection_busy = datetime(1990,1,1,1,1,1,1)

    shieldcharge_busy = pdata["shieldcharge_busy"]
    if shieldcharge_busy is None:
        shieldcharge_busy = datetime(1990,1,1,1,1,1,1)

    if not pdata["shieldcharged"]:
        print("cannot enable protection. It must be recharged")
        return(False)
 
    # get the new time until the building will be busy:
    protect_time = timedelta(float(buildinglevel * 2.4)/(24))
    busy_until = time_now + protect_time
    # Update the database with the new data
        
    table = connection["planets"]
    table.update({"id": planetid, "shieldprotection_busy": (busy_until), "shieldcharged": False}, ["id"])    
    
    table = connection["transactions"]
    table.update({"id": transaction_id, "tr_status": 1}, ["id"])  

    return True
    
def upgrade(planetid,building, parameter, time_now, trx_id, transaction_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    # get the planet data from the database    
    connection = connectdb()
    table = connection["planets"]
    pdata = table.find_one(id=planetid)

    if pdata is None:
        print("Could not find planetid %s" % str(planetid))
        return (False)          
    planetowner = pdata["user"]
    
    table = connection['users']
    userdata = table.find_one(username=planetowner)
    if userdata is None:
        print("Could not find user %s" % user)        
        return False    
       
    #Check which level is the building that should be updated
    (building_level, busy_parameter, skill_name) = get_building_parameter(building)
    if building_level is None:
        print("Unkown building %s" % building)
        return False

    buildinglevel = pdata[building_level]
    if buildinglevel is None:
        buildinglevel = 0
    new_building_level = int(int(buildinglevel) +1)

    # calculate the costs for the upgrade
    if building not in ["shipyard", "oredepot", "coaldepot", "copperdepot", "uraniumdepot", "base",
                        "researchcenter", "oremine", "coalmine", "coppermine", "uraniummine",
                        "ore", "coal", "copper", "uranium", "bunker", "shieldgenerator"]:
        print("Building %s not known" % building)
        return False
    if building in ["bunker"] and time_now < datetime(2019, 5, 9, 10, 0, 0):
        print("Building %s does not exists in the game right now." % building)
        return False
    if building in ["shieldgenerator"] and time_now < datetime(2019, 5, 25, 0, 0, 0):
        print("Building %s does not exists in the game right now." % building)
        return False        
    if str(new_building_level) not in upgrade_costs[building]:
        print("Upgrade %s is not possible, as %s does not exists in upgrade costs" % (building, str(new_building_level)))
        return False
    upgrade_building_costs = upgrade_costs[building][str(new_building_level)]

    coal_costs = upgrade_building_costs['coal']
    ore_costs = upgrade_building_costs['ore']
    copper_costs = upgrade_building_costs['copper']
    uranium_costs = upgrade_building_costs['uranium']

    # get the current level of available resources from the database
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(planetid, parameter, time_now)
    if pdata[busy_parameter] is None:
        busy_time = datetime(1990,1,1,1,1,1,1)
    else:
        busy_time = pdata[busy_parameter]
    
    building_skill_level = userdata[skill_name]
    if building_skill_level is None:
        building_skill_level = 0
    if new_building_level > int(building_skill_level):
        print("Lacking %s skill level (%d is required)" % (skill_name, new_building_level))
        return False        
    
    if time_now < busy_time:
        print("cannot upgrade this building. It is currently busy, %.2f min to go" % ((time_now - busy_time).total_seconds() / 60))
        return(False)
    # get the new time until the building will be busy:
    upgrade_time = timedelta(float(upgrade_building_costs['upgrade_time'])/(60*60*24) * (1 - 0.01 * level_base))
    busy_until = time_now + upgrade_time

    # check if the necessary resouces are available
    if ((float(new_qty_coal)>=float(coal_costs)) and (float(new_qty_ore)>=float(ore_costs)) and (float(new_qty_copper)>=float(copper_costs)) and (float(new_qty_uranium)>= float(uranium_costs))):
        final_qty_coal = new_qty_coal - coal_costs
        final_qty_ore = new_qty_ore - ore_costs
        final_qty_copper = new_qty_copper - copper_costs
        final_qty_uranium = new_qty_uranium - uranium_costs
    else:
        print("Lacking resources")
        return False

    # Update the database with the new data
    connection.begin()
    try:
        table = connection["planets"]
        table.update({"id": planetid, str(busy_parameter): (busy_until),
                              "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper,
                              "qyt_uranium": final_qty_uranium, "last_update": (time_now)}, ["id"])    
        table = connection["virtualops"]    
        table.insert({"tr_status":0, "tr_type":"finishbuilding", "tr_var1": planetid, "tr_var2": building, "tr_var3":str(new_building_level),
                      "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until, "user":planetowner})
        table = connection["transactions"]
        table.update({"id": transaction_id, "tr_status": 1}, ["id"])  
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False
    
    return True

def gift_item(uid, target, parameter, time_now, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]       
    
    # get the planet data from the database
    # Connect to the database
    connection = connectdb()
    table = connection["items"]
    itemdata = table.find_one(uid=uid)
    if itemdata is None:
        print("Error getting the item from the database")
        return False
    if itemdata["activated_trx"] is not None:
        print("Item is already activated")
        return False   
    if itemdata["for_sale"] == 1:
        print("Item is listed for sale")
        return False          
    table = connection["shop"]
    shopdata = table.find_one(itemid=itemdata["itemid"])
    if shopdata is None:
        print("Error getting the itemid from the shop database")
        return False    
    if not shopdata["tradeble"]:
        print("Item is not tradable/giftable")
        return False       
    target = target.lower().strip()
    existinguser = checkifuser(target)
    
    if existinguser:    
        print ("User found in the DB: " +str(existinguser))
        table = connection["items"]
        table.update({"uid":uid, "last_owner": itemdata["owner"], "owner": target, "item_gifted_at": (time_now)}, ["uid"])
    else:
        print ("User not found in the DB: " +str(target))
        return False

    return True


def transfer_stardust(username, amount, target, parameter, time_now, trx_id):
    connection = connectdb()
    table = connection["users"]
    user = table.find_one(username=username)
    if user is None:
        print("Error getting the user from the database")
        return False
  
    target = target.lower().strip()
    if target == username:
        print("Cannot send stardust to yourself")
        return False        
    
    table = connection["users"]
    target_user = table.find_one(username=target)
    if target_user is None:
        print("Error getting the user from the database")
        return False
    try:
        amount = float(amount)
    except:
        print("Could not parse amount")
        return False
    
    int_amount = int(amount * 1e8)
    if user["stardust"] is None or user["stardust"] < int_amount:
        print("Can not send stardust")
        return False
    if int_amount <= 0:
        print("Can not send stardust")
        return False  

    connection.begin()
    try:     
        table = connection["users"]
        table.update({"id": user["id"], "stardust":user["stardust"] - int_amount }, ["id"])
        if target_user["stardust"] is None:
            table.update({"id": target_user["id"], "stardust": int_amount }, ["id"])
        else:
            table.update({"id": target_user["id"], "stardust": target_user["stardust"] + int_amount }, ["id"]) 
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "transfer", "tr_status": 1, "date": time_now,
                    "from_user":username, "to_user":target, "amount":int_amount})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False       

    return True


def rename_planet(uid, new_name, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()
    legendary_planets_uid = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008']
    if new_name is None or new_name == "":
        print("Empty name")
        return False
    if not bool(re.match('^[a-zA-Z0-9\.\-\#\_]+$', new_name)):
        print("Only A-Za-z0-9.-_#")
        return False        
    if uid in legendary_planets_uid:
        print("Legendary planet cannot be renamed")
        return False
    if len(new_name) > 20:
        print("new name has %d > 20 chars" % len(new_name))
        return False
    table = connection["planets"]
    pdata = table.find_one(id=uid)

    if pdata is None:
        print("Could not find planetid %s" % str(uid))
        return (False)       

    table = connection['planets']
    data = dict(id=uid, name=new_name)
    table.update(data,['id'])

    return True

def update_shop(item_id, parameter_name, new_value, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()
    table = connection["shop"]
    shop_data = table.find_one(itemid=item_id)
    if shop_data is None:
        print("Could not find item %s" % item_id)
        return False
    if parameter_name not in shop_data:
        print("Could not find parameter %s" % parameter_name)
        return False
    if parameter_name not in ["sales_per_day", "max_supply", "price"]:
        print("Parameter %s is not supported" % parameter_name)
        return False
    table.update({"itemid": item_id, parameter_name: new_value}, ["itemid"])
    return True

def new_season(season_name, duration_days, steem_rewards, leach_rate, deploy_rate, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()
    table = connection["season"]
        
    last_season = table.find_one(order_by="-end_date")
    if last_season is not None:
        last_season_id = int(last_season["id"])
    else:
        last_season_id = 0
    if last_season is not None and last_season["end_date"] > time_now:
        print("Old season is still running")
        return False
    try:
        duration_days = float(duration_days)
        steem_rewards = float(steem_rewards)
        leach_rate = float(leach_rate)
        deploy_rate = float(deploy_rate)
    except:
        print("Wrong parameters")
        return False  

    end_date = time_now + timedelta(days=duration_days)

    new_season_id = last_season_id + 1
    if new_season_id is None:
        print("Could not calculate the new season_id.")
        return False

    table.insert({"start_date": time_now, "end_date": end_date,
                    "steem_rewards": steem_rewards, "leach_rate": leach_rate, "deploy_rate": deploy_rate, "name": season_name})

    table = connection["virtualops"]    
    table.insert({"tr_status":0, "tr_type":"finishseason", "tr_var1": new_season_id ,
                  "date": time_now, "parent_trx": trx_id, "trigger_date": end_date, "user": "nextcolony"})

    return True

def finish_season(season_id, parameter, time_now, block_num, trx_id):
    print("finish_season")
    connection = connectdb()
    table = connection["season"]
    last_season = table.find_one(order_by="-end_date")
    if last_season is not None:
        last_season_id = int(last_season["id"])
    if season_id is not None:
        season_id = int(season_id)
    else:
        season_id = 0

    if season_id == last_season_id:
        table = connection["asks"]
        for ask in table.find(subcategory="Yamato", cancel_trx=None, buy_trx=None, sold=None, failed=None):
            ask_id = ask["id"]
            uid = ask["uid"]
            yamato_type = ask["type"]
            if yamato_type != "yamato":
                table = connection["asks"]
                table.update({"id": ask_id, "cancel_trx": trx_id, "failed": time_now}, ["id"])
                table = connection["ships"]
                table.update({"id":uid, "for_sale": 0}, ["id"])

        table = connection["ships"]
        for ship in table.find(type="yamato1"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato2"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato3"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])
        for ship in table.find(type="yamato4"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])      
        for ship in table.find(type="yamato5"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])   
        for ship in table.find(type="yamato6"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato7"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato8"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])
        for ship in table.find(type="yamato9"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])      
        for ship in table.find(type="yamato10"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])   
        for ship in table.find(type="yamato11"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato12"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato13"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])
        for ship in table.find(type="yamato14"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])      
        for ship in table.find(type="yamato15"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])   
        for ship in table.find(type="yamato16"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato17"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id']) 
        for ship in table.find(type="yamato18"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])
        for ship in table.find(type="yamato19"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])      
        for ship in table.find(type="yamato20"):
            shipid = ship["id"]
            table.update({"id": str(shipid), "type": "yamato"},['id'])
    else:
        print("Seasons are not matching. Nothing done.")  
        return False                                                    
    return True    

def upgrade_yamato(username, planetid, shiptype, parameter, time_now, block_num, trx_id):
    print("upgrade_yamato")
    connection = connectdb()
    #get the upgrade costs
    upgrade_costs = parameter["upgrade_costs"]

    # get planet data
    table = connection["planets"]
    planetdata = table.find_one(id=planetid)
    if planetdata is None:
        print("No planet found.")
        return False
    if planetdata["for_sale"] == 1:
        print("Planet for sale, can't start missions.")
        return False    
    startplanet = planetdata["startplanet"]
    ship_cords_hor = planetdata["cords_hor"]
    ship_cords_ver = planetdata["cords_ver"]
    planetowner = planetdata["user"]
    level_base = planetdata["level_base"]

    # get the right shipid
    table = connection["ships"]
    shipid = None
    shipdata = table.find_one(type=shiptype, user=planetowner, cords_hor=ship_cords_hor, cords_ver=ship_cords_ver, busy_until={'<': time_now}, mission_busy_until={'<': time_now}, for_sale=0)
    if shipdata is not None:
        shipid = shipdata["id"]
    else:
        shipid = None       
    if shipid is None:
        print("No free yamato %s was found." % shiptype)
        return False
    if shipdata["for_sale"] == 1:
        print("Can't upgrade yamato listed for sale")
        return False

    # Check for active upgrade yamato missions
    table = connection["missions"]
    active_mission = table.find_one(user=planetowner, cords_hor_dest=ship_cords_hor, cords_ver_dest=ship_cords_ver, mission_type="upgradeyamato", cancel_trx=None, busy_until_return={'>': time_now})
    if active_mission is not None:
        print("You can't start more than one Upgrade Yamato Missions")
        return False

    # Check available Missions
    table_user = connection["users"]
    userdata = table_user.find_one(username=planetowner)
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"]   
    
    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > time_now:
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=planetowner, cords_hor=ship_cords_hor ,cords_ver=ship_cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > time_now:
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > time_now:
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    if time_now < datetime(2019, 11, 20, 20, 30, 30):
        if startplanet is not None and int(startplanet) == 1:
            allowed_missions += 1
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        if allowed_planet_missions <= running_planet_missions:
            print("%d/%d planet missions are active, aborting..." % (running_planet_missions, allowed_planet_missions))
            return False     
    if allowed_missions <= running_missions:
        print("%d/%d user missions are active, aborting..." % (running_missions, allowed_missions))
        return False
    
    # Check for siege
    siege_list = []
    for mission in table.find(mission_type="siege", cords_hor_dest=ship_cords_hor, cords_ver_dest=ship_cords_ver, cancel_trx=None, order_by="-busy_until"):
        if mission["busy_until"] > time_now:
            continue
        if mission["busy_until_return"] < time_now and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        if mission["returning"] and time_now > datetime(2019, 7, 1, 15, 40, 0):
            continue
        siege_list.append({"mission_id": mission["mission_id"], "user": mission["user"]})
    
    if len(siege_list) > 0:
        print("Siege missions found: %s" % str(siege_list))
        return False  

    # check if the user exists and is the owner of the ship
    table = connection["users"]
    userdata = table.find_one(username=username)
    if userdata is None:
        errormsg = ("User %s does not exists" % target)
        print(errormsg)
        return False
    if planetowner != username:
        print ("User %s is not the owner of this ship" % username)
        return False
    if userdata["stardust"] is not None:
        stardust_balance = int(userdata["stardust"])
    else: 
        stardust_balance = 0

    # check which type of ship is tried to be upgraded
    if shipdata is None:
        print("Ship could could not be found %s" % itemid)
        return False  
    shiptype = shipdata["type"]    
    if shiptype.startswith("yamato") == False:
        print ("Ship is not a Yamato and thus not upgradable.")
        return False
    
    # check if there is an active season (else reject upgrades)
    table = connection["season"]
    season = table.find_one(end_date={'>': time_now}, start_date={'<': time_now})
    if season is None:
        print("Currently no active season. An upgrade is thus not possible")
        return False 
    else:
        season_id = season["id"]

    # get shiptype to upgrade to
    if shiptype[6:] is not None and shiptype[6:] != "":
        tier = int(shiptype[6:])
    else:
        tier = 0
    if tier == 20:
        print("Can't upgrade tier 20 yamato any higher.")
        return False
    target_ship_type = "yamato"+str(tier+1)
    print (target_ship_type)
    (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research,level_shipyard) = get_resource_levels(planetid, parameter, time_now)
     
    # check if the amount of resources on the planet is sufficient
    if target_ship_type in upgrade_costs:
        build_costs = upgrade_costs[target_ship_type]["1"]
    else:
        print ("Error! Upgrade Costs not found")
        return False 
    coal_costs = build_costs["coal"]
    ore_costs = build_costs["ore"]
    copper_costs = build_costs["copper"]
    uranium_costs = build_costs["uranium"]
    if build_costs["stardust"] is not None:
        stardust_costs = int(build_costs["stardust"])
    else:
        stardust_costs = 0
    build_time = timedelta(float(build_costs['upgrade_time'])/(60*60*24) * (1 - 0.01 * level_shipyard))
    busy_until = time_now + build_time    

    if new_qty_coal < coal_costs or new_qty_ore < ore_costs or new_qty_copper < copper_costs or new_qty_uranium < uranium_costs or stardust_balance < stardust_costs:
        print ("Error! Not enough ressources or stardust")
        return False 

    # deduct costs/sd
    print ("Amount of resources is sufficient")
    fin_qty_coal = float(new_qty_coal) - float(coal_costs)
    fin_qty_ore = float(new_qty_ore) - float(ore_costs)
    fin_qty_copper = float(new_qty_copper) - float(copper_costs)
    fin_qty_uranium = float(new_qty_uranium) - float(uranium_costs)
    fin_qty_stardust = int(stardust_balance) - int(stardust_costs)

    # create mission entries
    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    mission_id = uid_from_seed("M-")
    print(mission_id)  
    ships = {shiptype: 1}  

    connection.begin()
    try:
        table = connection["planets"]
        table.update({"id": planetid, "qyt_coal":fin_qty_coal, "qyt_ore": fin_qty_ore, "qyt_copper": fin_qty_copper, "qyt_uranium":fin_qty_uranium, "last_update": time_now}, ["id"])
        table = connection["users"]
        table.update({"stardust": fin_qty_stardust, "id": userdata["id"]}, ["id"])    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "mission_id": mission_id, "tr_type": "yamato", "tr_status": 1, "date": time_now, "from_user":username, "amount":stardust_costs})
        table = connection["missions"]
        table.insert({"mission_id": mission_id, "user": planetowner, "mission_type": "upgradeyamato",  "date": time_now, "busy_until": time_now,
                      "busy_until_return": busy_until, "ships": json.dumps(ships), "cords_hor": ship_cords_hor,
                      "cords_ver": ship_cords_ver, "cords_hor_dest": ship_cords_hor, "cords_ver_dest": ship_cords_ver,
                      "qyt_coal": 0, "qyt_ore": 0, "qyt_copper": 0,
                      "qyt_uranium": 0}) 
        table_ships = connection['ships']    
        table_ships.update({"id": str(shipid), "cords_hor": ship_cords_hor, "cords_ver": ship_cords_ver,
                            "mission_busy_until": busy_until, "position": 1, "qyt_uranium": 0,
                            "mission_id": mission_id, "last_update": time_now},['id'])
        table = connection["virtualops"]    
        table.insert({"tr_status":0, "tr_type":"finishyamato", "tr_var1": shipid, "tr_var2": ship_cords_hor, "tr_var3":ship_cords_ver, "tr_var4": mission_id, "tr_var5": season_id,
                      "date": time_now, "parent_trx": trx_id, "trigger_date": busy_until, "user":planetowner, "mission_id": mission_id})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False

    return True
    
def finish_yamato(shipid, ship_cords_hor, ship_cords_ver, mission_id, season_id, parameter, time_now, block_num, trx_id):
    print("finish_yamato")
    connection = connectdb()
    upgrade_costs = parameter["upgrade_costs"]
    
    # Check Mission
    table = connection["missions"]
    mission_data = table.find_one(mission_id=mission_id)
    if mission_data is None:
        print("No mission with id %s" % mission_id)
        return False

    # check if there is an active season (else reject upgrades)
    table = connection["season"]
    season = table.find_one(id=season_id, end_date={'>': time_now}, start_date={'<': time_now})
    if season is None:
        print("The season of the upgrade is not active anymore. An upgrade is thus not possible.")
        return False 

    # Calculate new tier
    table = connection['ships']
    ship = table.find_one(id=shipid)
    if ship is None:
        print("No ship to upgrade")
        return False
    user = ship["user"]
    shiptype = ship["type"]
    if shiptype[6:] is not None and shiptype[6:] != "":
        tier = int(shiptype[6:])
    else:
        tier = 0
    if tier == 20:
        print("Can't upgrade tier 20 yamato any higher.")
        return False
    newtier = "yamato"+str(tier+1)

    # Update seasonranking
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None:
        print("No season found.")
        return False
    if last_season is None or last_season["end_date"] < datetime.utcnow():
        current_season = None
    else:
        current_season = last_season
    
    if current_season is not None:
        season_id = current_season["id"]
    else:
        season_id = None

    build_costs = upgrade_costs[newtier]['1']
    reward_point = build_costs["stardust"]
    
    if season_id is not None:
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=user)
        if ranking is not None:
            old_build_reward = ranking["build_reward"]
            old_total_reward = ranking["total_reward"]
        else:
            old_build_reward = 0
            old_total_reward = 0
        new_build_reward = old_build_reward + reward_point
        new_total_reward = old_total_reward + reward_point
        # Update Ranking
        if reward_point != 0:
            table_ranking.upsert({"season_id": season_id, "user": user, "last_update": time_now, "build_reward":new_build_reward, "total_reward": new_total_reward}, ["season_id", "user"])
    else:
        print("Can't upgrade out of season.")
        # Add result in activity
        table = connection["activity"]
        table.upsert({"user": user, "mission_id": mission_id, "type": "upgradeyamato", "date": time_now, "cords_hor": ship_cords_hor,
                            "cords_ver": ship_cords_ver, "result": "no_upgrade"}, ["mission_id"])                       

    # Upgrade by setting new tier type
    table.update({"id": str(shipid), "type": newtier},['id'])  

    # Add result in activity
    table = connection["activity"]
    table.upsert({"user": user, "mission_id": mission_id, "type": "upgradeyamato", "date": time_now, "cords_hor": ship_cords_hor,
                          "cords_ver": ship_cords_ver, "result": "yamato_upgraded"}, ["mission_id"])   

    return True

def gift_planet(uid, target, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()
    target = target.lower().strip()
    
    table = connection['users']
    userdata = table.find_one(username=target)
    if userdata is None:
        # connection.executable.close()
        print("Could not find user %s" % target)
        return False

    table = connection["planets"]
    pdata = table.find_one(id=uid)

    if pdata is None:
        print("Could not find planetid %s" % str(uid))
        return False

    if pdata["for_sale"] == 1:
        print("Planet is listed for sale, can't transfer")
        return False
        
    planetowner = pdata["user"]
    cords_hor = pdata["cords_hor"]
    cords_ver = pdata["cords_ver"]
    if time_now > datetime(2019,6,28, 7,0,0):
        
        table = connection["missions"]
        missions_list = []
        for row in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver, order_by='-busy_until'):
            if row['busy_until_return'] is not None and row['busy_until_return'] < time_now:
                continue
            elif row['busy_until_return'] is None and row['busy_until'] < time_now:
                continue        
            missions_list.append(row)
       
        if len(missions_list) > 0:
            print("Could not gift planet %s, %d missions are active" % (uid, len(missions_list)))
            return (False)

    if time_now > datetime(2019,6,28, 7,0,0) and time_now < datetime(2019, 6, 28, 9, 0, 0):
        table = connection["ships"]
        n_ships = table.count(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver)
        if n_ships > 0:
            print("Could not gift planet %s, %d ships still on planet" % (uid, n_ships))
            return (False)        
    
    legendary_planets_uid = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008']
    
    # check if the amount of resources on the planet is sufficient
    stardust_costs = 100000000000
    # check if the user exists and is the owner of the ship
    table = connection['users']
    ownerdata = table.find_one(username=planetowner)
    if ownerdata["stardust"] is not None:
        stardust_balance = int(ownerdata["stardust"])
    else: 
        stardust_balance = 0
    if stardust_balance < stardust_costs:
        print ("Error! Not enough stardust")
        return False 
    fin_qty_stardust = int(stardust_balance) - int(stardust_costs)    

    if uid not in legendary_planets_uid and pdata["startplanet"] == 1:
        print("Could not gift startplanet %s" % str(uid))
        # connection.executable.close()
        return (False)
    elif uid in legendary_planets_uid and pdata["startplanet"] == 1:
    
        reg_h=0
        reg_v=0
        init_lvl_copper = 0
        init_lvl_coal = 0
        init_lvl_ore = 0
        init_lvl_uranium = 0
        init_lvl_copperdepot = 0
        init_lvl_coaldepot = 0
        init_lvl_oredepot = 0
        init_lvl_uraniumdepot = 0
        
        init_lvl_base = 1
        init_lvl_base_skill = 1
        
        init_qty_copper = 29
        init_qty_coal = 119
        init_qty_ore = 59
        init_qty_uranium = 14        
        
        seed = get_seed(block_num, trx_id)           
        set_seed(seed)
        planetname = 'Alpha'
        img_id = 0
        bonus = 1
        planet_type = 1
        new_uid = None   
    
    
        table = connection['planets']
        coords_list = []
        solarsystem_list = []
        region_list = []
        for p in table.all():
            x_solarsystem, y_solarsystem = coords_to_solarsystem(int(p["cords_hor"]), int(p["cords_ver"]))
            x_region, y_region = coords_to_region(int(p["cords_hor"]), int(p["cords_ver"]))
            coords_list.append((int(p["cords_hor"]), int(p["cords_ver"])))
            solarsystem_list.append((x_solarsystem, y_solarsystem))
            if p["bonus"] == 4:
                region_list.append((x_region, y_region))        

        donat_ring_index = 0
        donat_ring_list = [3, 5]
        region_found = False
        x_solarsystem =None
        galaxy_x = 0
        galaxy_y = 0        
        add_legendary = False
        while x_solarsystem is None:
            while not region_found and donat_ring_index < len(donat_ring_list):
                x_solarsystem, y_solarsystem = get_free_solarsystem_in_donat(coords_list, solarsystem_list, region_list, galaxy_x, galaxy_y, donat_ring_list[donat_ring_index], add_legendary)
                
                if x_solarsystem is None:
                    print("using donat ring %d is full " % donat_ring_list[donat_ring_index])
                    donat_ring_index += 1
                else:
                    region_found = True
            if x_solarsystem is None:
                galaxy_x = 1
                galaxy_y = 1                
        if x_solarsystem is None:
            print("Could not find a region")
            return False
        print("found solarsystem %d, %d" % (x_solarsystem, y_solarsystem))
        x, y = get_random_coords_in_solarsystem(x_solarsystem, y_solarsystem)
        x_region, y_region =  coords_to_region(x,y)
        # (x,y) = find_starterplanet_coords(reg_h,reg_v)
        print ("Coordinates for the new planet: %d, %d in region %d, %d " % (x, y, x_region, y_region))
    
        if new_uid is None:
            new_uid = uid_from_seed("P-")
    
        create_planet(x,y, new_uid, time_now, block_num, trx_id)        
        table = connection["planets"]
        table.update({"id": new_uid, "img_id": img_id, "user": planetowner, "name": planetname, "planet_type": planet_type, "bonus": bonus, "qyt_uranium": init_qty_uranium,
                      "qyt_ore": init_qty_ore, "qyt_copper": init_qty_copper, "qyt_coal": init_qty_coal,
                      "level_uranium": init_lvl_uranium, "level_ore": init_lvl_ore, "level_copper": init_lvl_copper,
                      "level_coal": init_lvl_coal, "level_base": init_lvl_base, "level_coaldepot": init_lvl_coaldepot, 
                      "level_uraniumdepot": init_lvl_uraniumdepot, "level_oredepot": init_lvl_oredepot, "level_copperdepot": init_lvl_copperdepot,
                      "last_update": (time_now), "date_disc": (time_now),
                      "cords_hor": x, "cords_ver": y, "startplanet": True}, ["id"])
    
        update_resource_rate(new_uid, parameter, time_now)
    
    # Update Yamato Ranking for transferred ships
    # Get current season            
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None or last_season["end_date"] < time_now:
        current_season = None
    else:
        current_season = last_season
    if current_season is not None:
        season_id = int(current_season["id"])
        deploy_rate = current_season["deploy_rate"]
        if deploy_rate is not None:
            deploy_rate = float(deploy_rate)
        else:
            deploy_rate = 0
    else:
        season_id = None
        deploy_rate = None 

    if season_id is not None:       
        # Get Sender (sender) reward
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=planetowner)
        if ranking is not None:
            old_sender_build_reward = int(ranking["build_reward"])
            old_sender_total_reward = int(ranking["total_reward"])
        else:
            old_sender_build_reward = 0
            old_sender_total_reward = 0

        table = connection["ships"]
        delta_build_reward = 0
        for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
            shipid = ship["id"]
            shiptype = ship["type"]
            if shiptype[:6] == "yamato":
                if shiptype[6:] is not None and shiptype[6:] != "":
                    shiptier = int(shiptype[6:])
                else:
                    continue
                # Loop through all tiers with stardust to sum up total reward to tranfer   
                for tier in range(1, shiptier+1):   
                    current_shiptype = "yamato"+str(tier)             
                    build_costs = upgrade_costs[current_shiptype]['1']
                    if build_costs["stardust"] is not None:
                        delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                    else:
                        delta_build_reward = delta_build_reward + 0
        if delta_build_reward != 0:                
            new_sender_build_reward = old_sender_build_reward - delta_build_reward
            new_sender_total_reward = old_sender_total_reward - delta_build_reward               
            table_ranking.upsert({"season_id": season_id, "user": planetowner, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"])  

    if time_now > datetime(2019, 6, 28, 9, 0, 0):
        table = connection["ships"]
        n_ships = table.count(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver)
        if n_ships > 0:
            connection.begin()
            for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
                table.update({"id": ship["id"], "user": target}, ["id"])
            connection.commit()  

    table = connection['planets']
    if target == "null":        
        data = dict(id=uid,user="null",startplanet=False,abandoned=True, qyt_uranium=0, qyt_ore=0, qyt_copper=0, qyt_coal=0, rate_coal=0, rate_ore=0, rate_copper=0, rate_uranium=0,
        depot_coal=0, depot_ore=0, depot_copper=0, depot_uranium=0, level_uranium=0, level_ore=0, level_copper=0, level_coal=0, level_ship=0, ship_current=0, level_base=0, level_bunker=0,
        level_shieldgenerator=0, level_research=0, level_coaldepot=0, level_oredepot=0, level_copperdepot=0, level_uraniumdepot=0, level_shipyard=0, shieldcharged=0,last_update=time_now,qyp_uranium=0,
        boost_percentage=0)
        table.update(data,['id'])
    else:
        data = dict(id=uid,user=target,startplanet=False)
        table.update(data,['id'])
    # costs
    connection.begin()
    try: 
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "fee", "tr_status": 1, "date": time_now, "from_user":planetowner, "amount":stardust_costs})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False   
    # ranking
    update_ranking_user(target, time_now)
    update_ranking_user(planetowner, time_now)
    return True


def activate(uid, target, parameter, time_now, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]       
    
    # get the planet data from the database
    # Connect to the database
    connection = connectdb()
    table = connection["items"]
    itemdata = table.find_one(uid=uid)
    if itemdata is None:
        print("Error getting the item from the database")
        return False
    if itemdata["activated_trx"] is not None:
        print("Item is already activated")
        return False     
    if itemdata["for_sale"] == 1:
        print("Item is listed for sale")
        return False           
  
    #Check which level is the building that should be updated
    
    table = connection["shop"]
    shopdata = table.find_one(itemid=itemdata["itemid"])
    if shopdata is None:
        print("Error getting the itemid from the shop database")
        return False    
    if not shopdata["activateable"]:
        print("Item is not activateable!")
        return False            
    
    if shopdata["apply_to"] =="planet":
        table = connection["planets"]
        planetdata = table.find_one(id=target)
        if planetdata is None:
            print("Error getting the planet %s from the database" % str(target))
            return False
        if planetdata["user"] != itemdata["owner"]:
            print("Planet owner and item owner are not equal")
            return False
        (new_qty_coal,new_qty_ore,new_qty_copper,new_qty_uranium,level_base,level_research, level_shipyard) = get_resource_levels(target, parameter, time_now)
        if shopdata["coal"] is not None:
            final_qty_coal = new_qty_coal + shopdata["coal"]
        else:
            final_qty_coal = new_qty_coal

        if shopdata["ore"] is not None:
            final_qty_ore = new_qty_ore + shopdata["ore"]
        else:
            final_qty_ore = new_qty_ore

        if shopdata["copper"] is not None:
            final_qty_copper = new_qty_copper + shopdata["copper"]
        else:
            final_qty_copper = new_qty_copper
 
        if shopdata["uranium"] is not None:
            final_qty_uranium = new_qty_uranium + shopdata["uranium"]
        else:
            final_qty_uranium = new_qty_uranium
        
        if shopdata["boost_percentage"] is not None:
            boost_percentage = shopdata["boost_percentage"]
            activate_booster = True
        else:
            activate_booster = False
            
        if shopdata["blueprint"] is not None:
            blueprint = shopdata["blueprint"]
            activate_blueprint = True
            if planetdata["blueprints"] is not None and blueprint in planetdata["blueprints"].split(","):
                print("Blueprint %s already activated" % blueprint)
                return False
            if planetdata["blueprints"] is None or len(planetdata["blueprints"]) == 0:
                blueprints = blueprint
            else:
                blueprints = planetdata["blueprints"] + "," + blueprint
        else:
            activate_blueprint = False        
    
        if planetdata["planet_type"] == 1 and activate_booster and boost_percentage > 0 and time_now > datetime(2019,4,25,6,49,0):
            print("Booster is not activatable on atmosphere")
            return False
        
        table = connection["items"]
        table.update({"uid":uid, "activated_trx": trx_id, "activated_date": (time_now), "activated_to":target}, ["uid"])
        
        table = connection["planets"]
        if activate_booster:
            table.update({"id":target, "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper, "qyt_uranium": final_qty_uranium,
                          "boost_percentage": boost_percentage, "booster_activate_trx": trx_id, "last_update": time_now}, ["id"])
        elif activate_blueprint:
            table.update({"id":target, "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper, "qyt_uranium": final_qty_uranium,
                          "blueprints": blueprints, "last_update": time_now}, ["id"])
            
        else:
            table.update({"id":target, "qyt_coal": final_qty_coal, "qyt_ore": final_qty_ore, "qyt_copper": final_qty_copper,
                          "qyt_uranium": final_qty_uranium, "last_update": time_now}, ["id"])            
        update_resource_rate(target, parameter, time_now)
    else:
        return False

    return True

def adduser(name, parameter, time_now, block_num, trx_id):
    reg_h=0
    reg_v=0
    init_lvl_copper = 0
    init_lvl_coal = 0
    init_lvl_ore = 0
    init_lvl_uranium = 0
    init_lvl_copperdepot = 0
    init_lvl_coaldepot = 0
    init_lvl_oredepot = 0
    init_lvl_uraniumdepot = 0
    
    init_lvl_base = 1
    init_lvl_base_skill = 1
    init_lvl_missioncontrol_skill = None
    if time_now > datetime(2019, 11, 20, 20, 30, 30):
        init_lvl_missioncontrol_skill = 1
    
    init_qty_copper = 29
    init_qty_coal = 119
    init_qty_ore = 59
    init_qty_uranium = 14
    
    
    existinguser = checkifuser(name)
    print ("%s found in the DB: %s " % (name, str(existinguser)))
    if existinguser:
        print ("User is aready active in the game")
        return (False)
    
    
    seed = get_seed(block_num, trx_id)           
    set_seed(seed)    
    legendary_planets_uid = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008']
    if name == 'sternenkrieger':
        bonus = 4
        planet_type = 5
        planetname = "Venus XII"
        uid = '1000'
        img_id = 1000
    elif name == 'govinda71':
        bonus = 4
        planet_type = 5
        planetname = "Delta"
        uid = '1001'
        img_id = 1001
    elif name == 'reggaemuffin':
        bonus = 4
        planet_type = 5
        planetname = "Prometheus"
        uid = '1002'
        img_id = 1002
    elif name == 'urachem':
        bonus = 4
        planet_type = 5
        planetname = "Tartaros"
        uid = '1003'
        img_id = 1003
    elif name == 'mancer-sm-alt':
        bonus = 4
        planet_type = 5
        planetname = "Zyklop"
        uid = '1004'
        img_id = 1004
    elif name == 'uraniumfuture':
        bonus = 4
        planet_type = 5
        planetname = "Lightsaber"
        uid = '1005'
        img_id = 1005
    elif name == 'xx0xx':
        bonus = 4
        planet_type = 5
        planetname = "Drakon"
        uid = '1006'
        img_id = 1006  
    elif name == 'ngc':
        bonus = 4
        planet_type = 5
        planetname = "Tellus"
        uid = '1007'
        img_id = 1007    
    elif name == 'z8teyb289qav9z':
        bonus = 4
        planet_type = 5
        planetname = "Omega"
        uid = '1008'
        img_id = 1008            
    elif name == "nextcolony":
        bonus = 4
        planet_type = 1
        planetname = "Earth"
        uid = '1'
        img_id = 0
        x = 0
        y = 0
    else:
        planetname = 'Alpha'
        img_id = 0
        bonus = 1
        planet_type = 1
        uid = None   
    
    connection = connectdb()
    table = connection['planets']
    coords_list = []
    solarsystem_list = []
    region_list = []
    for p in table.all():
        x_solarsystem, y_solarsystem = coords_to_solarsystem(int(p["cords_hor"]), int(p["cords_ver"]))
        x_region, y_region = coords_to_region(int(p["cords_hor"]), int(p["cords_ver"]))
        coords_list.append((int(p["cords_hor"]), int(p["cords_ver"])))
        solarsystem_list.append((x_solarsystem, y_solarsystem))
        if p["bonus"] == 4:
            region_list.append((x_region, y_region))    
    

    donat_ring_index = 0
    donat_ring_list = [3, 5]
    region_found = False
    x_solarsystem =None
    # Switch to start in new Galaxy
    if time_now >= datetime(2019, 10, 27, 13, 13, 13):
        add_legendary = False
        galaxy_x = 1
        galaxy_y = 1
        galaxy_list = [(1,1), (1,-1), (-1,-1), (-1,1)]
        galaxy_count = 4
        galaxy_index = 0
    else:
        if uid in legendary_planets_uid:
            add_legendary = True
        else:
            add_legendary = False
        galaxy_x = 0
        galaxy_y = 0
        galaxy_list = [(0,0), (1,1), (1,-1), (-1,-1), (-1,1)]
        galaxy_count = 5
        galaxy_index = 0
    while x_solarsystem is None and galaxy_index < galaxy_count:
        while not region_found and donat_ring_index < len(donat_ring_list):
            x_solarsystem, y_solarsystem = get_free_solarsystem_in_donat(coords_list, solarsystem_list, region_list, galaxy_x, galaxy_y, donat_ring_list[donat_ring_index], add_legendary)
            
            if x_solarsystem is None:
                print("using donat ring %d is full " % donat_ring_list[donat_ring_index])
                donat_ring_index += 1
            elif uid in legendary_planets_uid:
                print("add legendary planet")
                region_found = True
            else:
                region_found = True
        if x_solarsystem is None:
            
            galaxy_index += 1
            galaxy_x = galaxy_list[galaxy_index][0]
            galaxy_y = galaxy_list[galaxy_index][1]
            donat_ring_index = 0
            print("Go to next galaxy: %d/%d" % (galaxy_x, galaxy_y))
    if x_solarsystem is None:
        print("Could not find a region")
        return False
    print("found solarsystem %d, %d, donat %d" % (x_solarsystem, y_solarsystem, donat_ring_list[donat_ring_index]))
    if planetname != "Earth":
        x, y = get_random_coords_in_solarsystem(x_solarsystem, y_solarsystem)
    x_region, y_region =  coords_to_region(x,y)
    print ("Coordinates for the new planet: %d, %d in region %d, %d " % (x, y, x_region, y_region))

    if uid is None:
        uid = uid_from_seed("P-")

    create_planet(x,y, uid, time_now, block_num, trx_id)
    
    table = connection["users"]
    table.insert({"username": name, "r_base": init_lvl_base_skill, "r_missioncontrol": init_lvl_missioncontrol_skill, "date": time_now})
    print("User created!")
    table = connection["planets"]
    table.update({"id": uid, "img_id": img_id, "user": name, "name": planetname, "planet_type": planet_type, "bonus": bonus, "qyt_uranium": init_qty_uranium,
                  "qyt_ore": init_qty_ore, "qyt_copper": init_qty_copper, "qyt_coal": init_qty_coal,
                  "level_uranium": init_lvl_uranium, "level_ore": init_lvl_ore, "level_copper": init_lvl_copper,
                  "level_coal": init_lvl_coal, "level_base": init_lvl_base, "level_coaldepot": init_lvl_coaldepot, 
                  "level_uraniumdepot": init_lvl_uraniumdepot, "level_oredepot": init_lvl_oredepot, "level_copperdepot": init_lvl_copperdepot,
                  "last_update": (time_now), "date_disc": (time_now),
                  "cords_hor": x, "cords_ver": y, "startplanet": True}, ["id"])

    update_resource_rate(uid, parameter, time_now)
    update_ranking_user(name, time_now)
    
    return (True)

def respawn(planet_id, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()

    table = connection["planets"]
    pdata = table.find_one(id=planet_id)
    uid = pdata["id"]

    if pdata is None:
        print("Could not find planetid %s" % str(uid))
        return (False)

    if pdata["bonus"] == 4:
        print("Legendary planets can't be respawned.")
        return (False)

    planetowner = pdata["user"]
    cords_hor = pdata["cords_hor"]
    cords_ver = pdata["cords_ver"]
      
    table = connection["missions"]
    missions_list = []
    for row in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver, order_by='-busy_until'):
        if row['busy_until_return'] is not None and row['busy_until_return'] < time_now:
            continue
        elif row['busy_until_return'] is None and row['busy_until'] < time_now:
            continue        
        missions_list.append(row)
    
    if len(missions_list) > 0:
        print("Could not respawn planet %s, %d missions are active" % (uid, len(missions_list)))
        return (False)    
    
    if pdata["startplanet"] != 1:
        print("Only starter planets can be respawn. Could not respawn planet: %s" % str(uid))
        return (False)
    
    # check if the user has enough stardust
    stardust_costs = 100000000000
    # check if the user exists and is the owner of the ship
    table = connection['users']
    ownerdata = table.find_one(username=planetowner)
    if ownerdata["stardust"] is not None:
        stardust_balance = int(ownerdata["stardust"])
    else: 
        stardust_balance = 0
    if stardust_balance < stardust_costs:
        print ("Error! Not enough stardust")
        return False 
    fin_qty_stardust = int(stardust_balance) - int(stardust_costs)   


    # Update Yamato Ranking for transferred ships
    # Get current season            
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None or last_season["end_date"] < time_now:
        current_season = None
    else:
        current_season = last_season
    if current_season is not None:
        season_id = int(current_season["id"])
        deploy_rate = current_season["deploy_rate"]
        if deploy_rate is not None:
            deploy_rate = float(deploy_rate)
        else:
            deploy_rate = 0
    else:
        season_id = None
        deploy_rate = None 

    if season_id is not None:       
        # Get Sender (sender) reward
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=planetowner)
        if ranking is not None:
            old_sender_build_reward = int(ranking["build_reward"])
            old_sender_total_reward = int(ranking["total_reward"])
        else:
            old_sender_build_reward = 0
            old_sender_total_reward = 0

        table = connection["ships"]
        delta_build_reward = 0
        for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
            shipid = ship["id"]
            shiptype = ship["type"]
            if shiptype[:6] == "yamato":
                if shiptype[6:] is not None and shiptype[6:] != "":
                    shiptier = int(shiptype[6:])
                else:
                    continue
                # Loop through all tiers with stardust to sum up total reward to tranfer   
                for tier in range(1, shiptier+1):   
                    current_shiptype = "yamato"+str(tier)             
                    build_costs = upgrade_costs[current_shiptype]['1']
                    if build_costs["stardust"] is not None:
                        delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                    else:
                        delta_build_reward = delta_build_reward + 0
        if delta_build_reward != 0:
            new_sender_build_reward = old_sender_build_reward - delta_build_reward
            new_sender_total_reward = old_sender_total_reward - delta_build_reward               
            table_ranking.upsert({"season_id": season_id, "user": planetowner, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"])
   
    # costs
    connection.begin()
    try:
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "fee", "tr_status": 1, "date": time_now, "from_user":planetowner, "amount":stardust_costs})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False  

    # Transfer Ships
    table = connection["ships"]
    n_ships = table.count(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver)
    if n_ships > 0:
        connection.begin()
        for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
            table.update({"id": ship["id"], "user": "null"}, ["id"])
        connection.commit()   
        
    # Transfer Planet    
    table = connection['planets']
    data = dict(id=uid,user="null",startplanet=False,abandoned=True, qyt_uranium=0, qyt_ore=0, qyt_copper=0, qyt_coal=0, rate_coal=0, rate_ore=0, rate_copper=0, rate_uranium=0,
    depot_coal=0, depot_ore=0, depot_copper=0, depot_uranium=0, level_uranium=0, level_ore=0, level_copper=0, level_coal=0, level_ship=0, ship_current=0, level_base=0, level_bunker=0,
    level_shieldgenerator=0, level_research=0, level_coaldepot=0, level_oredepot=0, level_copperdepot=0, level_uraniumdepot=0, level_shipyard=0, shieldcharged=0,last_update=time_now,qyp_uranium=0,
    boost_percentage=0)
    table.update(data,['id'])

    # Create new planet
    seed = get_seed(block_num, trx_id)           
    set_seed(seed)    
    planetname = 'Novum'
    img_id = 0
    bonus = 1
    planet_type = 1
    uid = None   

    reg_h=0
    reg_v=0
    init_lvl_copper = 0
    init_lvl_coal = 0
    init_lvl_ore = 0
    init_lvl_uranium = 0
    init_lvl_copperdepot = 0
    init_lvl_coaldepot = 0
    init_lvl_oredepot = 0
    init_lvl_uraniumdepot = 0
    
    init_lvl_base = 1
    init_lvl_base_skill = 1
    
    init_qty_copper = 29
    init_qty_coal = 119
    init_qty_ore = 59
    init_qty_uranium = 14
           
    connection = connectdb()
    table = connection['planets']
    coords_list = []
    solarsystem_list = []
    region_list = []
    for p in table.all():
        x_solarsystem, y_solarsystem = coords_to_solarsystem(int(p["cords_hor"]), int(p["cords_ver"]))
        x_region, y_region = coords_to_region(int(p["cords_hor"]), int(p["cords_ver"]))
        coords_list.append((int(p["cords_hor"]), int(p["cords_ver"])))
        solarsystem_list.append((x_solarsystem, y_solarsystem))    

    donat_ring_index = 0
    donat_ring_list = [3, 5]
    region_found = False
    x_solarsystem =None
    add_legendary = False
    galaxy_x = 1
    galaxy_y = 1
    galaxy_list = [(1,1), (1,-1), (-1,-1), (-1,1)]
    galaxy_count = 4
    galaxy_index = 0
    while x_solarsystem is None and galaxy_index < galaxy_count:
        while not region_found and donat_ring_index < len(donat_ring_list):
            x_solarsystem, y_solarsystem = get_free_solarsystem_in_donat(coords_list, solarsystem_list, region_list, galaxy_x, galaxy_y, donat_ring_list[donat_ring_index], add_legendary)
            
            if x_solarsystem is None:
                print("using donat ring %d is full " % donat_ring_list[donat_ring_index])
                donat_ring_index += 1
            else:
                region_found = True
        if x_solarsystem is None:
            
            galaxy_index += 1
            galaxy_x = galaxy_list[galaxy_index][0]
            galaxy_y = galaxy_list[galaxy_index][1]
            donat_ring_index = 0
            print("Go to next galaxy: %d/%d" % (galaxy_x, galaxy_y))
    if x_solarsystem is None:
        print("Could not find a region")
        return False
    print("found solarsystem %d, %d, donat %d" % (x_solarsystem, y_solarsystem, donat_ring_list[donat_ring_index]))
    if planetname != "Earth":
        x, y = get_random_coords_in_solarsystem(x_solarsystem, y_solarsystem)
    x_region, y_region =  coords_to_region(x,y)
    print ("Coordinates for the new planet: %d, %d in region %d, %d " % (x, y, x_region, y_region))

    if uid is None:
        uid = uid_from_seed("P-")

    create_planet(x,y, uid, time_now, block_num, trx_id)
    
    table = connection["planets"]
    table.update({"id": uid, "img_id": img_id, "user": planetowner, "name": planetname, "planet_type": planet_type, "bonus": bonus, "qyt_uranium": init_qty_uranium,
                  "qyt_ore": init_qty_ore, "qyt_copper": init_qty_copper, "qyt_coal": init_qty_coal,
                  "level_uranium": init_lvl_uranium, "level_ore": init_lvl_ore, "level_copper": init_lvl_copper,
                  "level_coal": init_lvl_coal, "level_base": init_lvl_base, "level_coaldepot": init_lvl_coaldepot, 
                  "level_uraniumdepot": init_lvl_uraniumdepot, "level_oredepot": init_lvl_oredepot, "level_copperdepot": init_lvl_copperdepot,
                  "last_update": (time_now), "date_disc": (time_now),
                  "cords_hor": x, "cords_ver": y, "startplanet": True}, ["id"])

    update_ranking_user(planetowner, time_now)
    
    return (True)

def burn(planet_id, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    skill_costs = parameter["skill_costs"]
    production_rates = parameter["production_rates"]
    connection = connectdb()

    table = connection["planets"]
    pdata = table.find_one(id=planet_id)
    uid = pdata["id"]

    if pdata is None:
        print("Could not find planetid %s" % str(uid))
        return (False)

    if pdata["for_sale"] == 1:
        print("Can't burn planets listed for sale")
        return False

    planetowner = pdata["user"]
    cords_hor = pdata["cords_hor"]
    cords_ver = pdata["cords_ver"]
      
    table = connection["missions"]
    missions_list = []
    for row in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver, order_by='-busy_until'):
        if row['busy_until_return'] is not None and row['busy_until_return'] < time_now:
            continue
        elif row['busy_until_return'] is None and row['busy_until'] < time_now:
            continue        
        missions_list.append(row)
    
    if len(missions_list) > 0:
        print("Could not burn planet %s, %d missions are active" % (uid, len(missions_list)))
        return (False)    
    
    if pdata["startplanet"] == 1:
        print("Can't burn starter planet. Could not burn planet: %s" % str(uid))
        return (False)

    if pdata["abandoned"] == 1:
        print("Can't burn abandoned again. Could not burn planet: %s" % str(uid))
        return (False)

    # Stardust to receive for burn
    bonus = pdata["bonus"]
    planet_type = pdata["planet_type"]
    print("Burning planet. Bonus: %s, Type: %s" % (str(bonus), str(planet_type)))
    stardust_income = get_burn_income(bonus, planet_type)
    # check if the user exists
    table = connection['users']
    ownerdata = table.find_one(username=planetowner)
    if ownerdata["stardust"] is not None:
        stardust_balance = int(ownerdata["stardust"])
    else: 
        stardust_balance = 0
    fin_qty_stardust = int(stardust_balance) + int(stardust_income)   


    # Update Yamato Ranking for transferred ships
    # Get current season            
    table_season = connection["season"]
    last_season = table_season.find_one(order_by="-end_date")
    if last_season is None or last_season["end_date"] < time_now:
        current_season = None
    else:
        current_season = last_season
    if current_season is not None:
        season_id = int(current_season["id"])
        deploy_rate = current_season["deploy_rate"]
        if deploy_rate is not None:
            deploy_rate = float(deploy_rate)
        else:
            deploy_rate = 0
    else:
        season_id = None
        deploy_rate = None 

    if season_id is not None:       
        # Get Sender (sender) reward
        table_ranking = connection['seasonranking']
        ranking = table_ranking.find_one(season_id=season_id,user=planetowner)
        if ranking is not None:
            old_sender_build_reward = int(ranking["build_reward"])
            old_sender_total_reward = int(ranking["total_reward"])
        else:
            old_sender_build_reward = 0
            old_sender_total_reward = 0

        table = connection["ships"]
        delta_build_reward = 0
        for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
            shipid = ship["id"]
            shiptype = ship["type"]
            if shiptype[:6] == "yamato":
                if shiptype[6:] is not None and shiptype[6:] != "":
                    shiptier = int(shiptype[6:])
                else:
                    continue
                # Loop through all tiers with stardust to sum up total reward to tranfer   
                for tier in range(1, shiptier+1):   
                    current_shiptype = "yamato"+str(tier)             
                    build_costs = upgrade_costs[current_shiptype]['1']
                    if build_costs["stardust"] is not None:
                        delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                    else:
                        delta_build_reward = delta_build_reward + 0
        if delta_build_reward != 0:
            new_sender_build_reward = old_sender_build_reward - delta_build_reward
            new_sender_total_reward = old_sender_total_reward - delta_build_reward               
            table_ranking.upsert({"season_id": season_id, "user": planetowner, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"])
   
    # income
    connection.begin()
    try:
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "burn", "tr_status": 1, "date": time_now, "to_user":planetowner, "amount":stardust_income})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False    

    # Transfer Ships
    table = connection["ships"]
    n_ships = table.count(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver)
    if n_ships > 0:
        connection.begin()
        for ship in table.find(user=planetowner, cords_hor=cords_hor, cords_ver=cords_ver):
            table.update({"id": ship["id"], "user": "null"}, ["id"])
        connection.commit()   
        
    # Transfer Planet    
    table = connection['planets']
    data = dict(id=uid,user="null",startplanet=False,abandoned=True, qyt_uranium=0, qyt_ore=0, qyt_copper=0, qyt_coal=0, rate_coal=0, rate_ore=0, rate_copper=0, rate_uranium=0,
    depot_coal=0, depot_ore=0, depot_copper=0, depot_uranium=0, level_uranium=0, level_ore=0, level_copper=0, level_coal=0, level_ship=0, ship_current=0, level_base=0, level_bunker=0,
    level_shieldgenerator=0, level_research=0, level_coaldepot=0, level_oredepot=0, level_copperdepot=0, level_uraniumdepot=0, level_shipyard=0, shieldcharged=0,last_update=time_now,qyp_uranium=0,
    boost_percentage=0)
    table.update(data,['id'])

    update_ranking_user(planetowner, time_now)
    
    return (True)

def issuestardust(amount, target, time_now, block_num, trx_id):
    connection = connectdb()

    try:
        amount = float(amount)
    except:
        print("Could not parse amount")
        return False
    
    int_amount = int(amount * 1e8)

    table = connection["users"]
    userdata = table.find_one(username=target)
    if userdata is None:
        print("User %s does not exists" % target)
        return False   
        
    if userdata["stardust"] is not None:
        stardust_balance = int(userdata["stardust"])
    else: 
        stardust_balance = 0
    fin_qty_stardust = int(stardust_balance) + int(int_amount)   

    connection.begin()
    try:
        table = connection["users"]
        table.update({"id": userdata["id"], "stardust": fin_qty_stardust}, ["id"])    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "issuestardust", "tr_status": 1, "date": time_now, "to_user":target, "amount":int_amount})
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False       

    return True

def ask(user, category, uid, price, market, parameter, time_now, block_num, trx_id):
    shipstats = parameter["shipstats"]
    cords_hor = None
    cords_ver = None
    img_id = None
    connection = connectdb()
    print("ask")
    # Price
    if price is None:
        print("No price")
        return False     
    try:
        price = float(price)
    except:
        print("Could not parse price")
        return False
    int_price = int(price * 1e8)
    int_fee_market = int(int_price * 0.04)
    int_fee_burn = int(int_price * 0.04)
    if int_price <= 0:
        print("Price can't be 0")
        return False
    if int_fee_market <= 0:
        print("Fee market can't be 0")
        return False
    if int_fee_burn <= 0:
        print("Fee market can't be 0")
        return False
    # Not more than 92233720368 stardust allowed (to fit into DB)
    if int_price > 9223372036854775807:
        print("Price is too high.")
        return False

    # Market
    if market is None:
        print("Missing market")
        return False
    if market is not None: 
        table = connection["users"]
        userdata = table.find_one(username=market)
        if userdata is None:
            print("Market %s does not exist" % market)
            return False   
    if market == user:
        print("Market and Seller can't be the same user")
        return False

    # Prepare Listing
    # ITEM
    if category == "item":
        table = connection["items"]
        item = table.find_one(uid=uid)  
        if item is None:
            print("Item %s does not exist" % uid)
            return False    
        if item["owner"] != user:
            print("You can only sell your own items")
            return False                        
        if item["activated_to"] is not None:
            print("You can't sell activated items")
            return False  
        if item["for_sale"] == 1:
            print("Item is listed for sale already")
            return False  
        subcategory = item["itemid"][:-3] # cut away last 3 chars like _01
        itype = item["itemid"]
    # PLANET    
    elif category == "planet":
        table = connection["planets"]
        planet = table.find_one(id=uid) 
        if planet is None:
            print("Planet %s does not exist" % uid)
            return False  
        if planet["user"] != user:
            print("You can only sell your own planets")
            return False  
        if planet["startplanet"] == 1:
            print("You can't sell your start planet")
            return False
        if planet["for_sale"] == 1:
            print("Planet is listed for sale already")
            return False      

        # Check outgoing missions
        cords_hor = planet["cords_hor"]
        cords_ver = planet["cords_ver"]       
        table = connection["missions"]
        missions_list = []
        for row in table.find(user=user, cords_hor=cords_hor, cords_ver=cords_ver, order_by='-busy_until'):
            if row['busy_until_return'] is not None and row['busy_until_return'] < time_now:
                continue
            elif row['busy_until_return'] is None and row['busy_until'] < time_now:
                continue        
            missions_list.append(row)   
        if len(missions_list) > 0:
            print("Could not sell planet %s, %d missions are active" % (uid, len(missions_list)))
            return (False) 
        # Check ships for sale
        table = connection["ships"]
        for ship in table.find(user=user, cords_hor=cords_hor, cords_ver=cords_ver):
            if ship["for_sale"] == 1:
                print("Can't sell a planet which has ships for sale")
                return False

        subcategory = planet["bonus"]
        itype = planet["planet_type"]
        img_id = planet["img_id"]
    # SHIP   
    elif category == "ship":
        planet_id = None
        planet_hor = None
        planet_ver = None
        table = connection["ships"]
        ship = table.find_one(id=uid) 
        if ship is None:
            print("Ship %s does not exist" % uid)
            return False  
        if ship["user"] != user:
            print("You can only sell your own ships")
            return False   
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % uid)
            return False
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % uid)
            return False   
        if ship["for_sale"] == 1:
            print("Ship is listed for sale already")
            return False        
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            return False          
        if planet_hor is None:
            print("Could not find planet_id")
            return False        
        planet_id = get_planetid (planet_hor, planet_ver)
        if planet_id is None:
            print("Could not find planet_id")
            return False     
        table = connection["planets"]
        planet_from_data = table.find_one(id=planet_id)
        if planet_from_data is None:
            print("Could not find planet_id")
            return False   
        subcategory = shipstats[ship["type"]]["class"]
        itype = ship["type"]
        cords_hor = planet_hor
        cords_ver = planet_ver
        if planet_from_data["for_sale"] == 1:
            print("Planet for sale, can't sell ships on it.")
            return False
    else:
        print("Not supported category: %s" % category)
        return False

    seed = get_seed(block_num, trx_id)    
    set_seed(seed)    
    ask_id = uid_from_seed("A-")
    print(ask_id)

    # List Sale
    table = connection["asks"]
    table.insert({"id": ask_id, "uid": uid, "category": category, "subcategory": subcategory, "type": itype, "uid": uid, "price": int_price,
                  "market": market, "date": time_now, "user": user, "fee_market": int_fee_market, "fee_burn": int_fee_burn, "cords_hor": cords_hor, "cords_ver": cords_ver, "img_id": img_id})
    if category == "item":
        table = connection["items"]
        table.update({"uid": uid, "for_sale": 1}, ["uid"]) 
    elif category == "ship":
        table = connection["ships"]
        table.update({"id": uid, "for_sale": 1}, ["id"]) 
    elif category == "planet":
        table = connection["planets"]
        table.update({"id": uid, "for_sale": 1}, ["id"]) 

    return True

def cancel_ask(ask_id, parameter, time_now, block_num, trx_id):
    connection = connectdb()
    print("cancel_ask")
    table = connection["asks"]
    ask_data = table.find_one(id=ask_id)
    # check
    if ask_data is None:
        print("No ask with id %s" % ask_id)
        return False
    if ask_data["sold"] is not None:
        print("Already sold, can not cancel")
        return False
    if ask_data["failed"] is not None:
        print("Can't cancel a failed ask.")
        return False    
    if ask_data["cancel_trx"] is not None:
        print("Can't cancel a cancelled ask.")
        return False      
    if ask_data["buy_trx"] is not None:
        print("Can't cancel a filled ask.")
        return False
    category = ask_data["category"]
    ask_id = ask_data["id"]
    uid = ask_data["uid"]
    table = connection["asks"]
    table.update({"id": ask_id, "cancel_trx": trx_id}, ["id"])
    if category == "ship":
        table = connection["ships"]
        table.update({"id": uid, "for_sale": 0}, ["id"]) 
    elif category == "item":
        table = connection["items"]
        table.update({"uid": uid, "for_sale": 0}, ["uid"])
    elif category == "planet":    
        table = connection["planets"]
        table.update({"id": uid, "for_sale": 0}, ["id"])

    return True

def fill_ask(user, ask_id, parameter, time_now, block_num, trx_id):
    upgrade_costs = parameter["upgrade_costs"]
    connection = connectdb()
    print("fill_ask")
    table = connection["asks"]
    ask_data = table.find_one(id=ask_id)
    if ask_data is None:
        print("Can't buy nothing")
        return False
    category = ask_data["category"]
    uid = ask_data["uid"]
    seller = ask_data["user"]
    market = ask_data["market"]

    # Check simple conditions
    if ask_data is None:
        print("No ask with id %s" % ask_id)
        return False
    if ask_data["sold"] is not None:
        print("Already sold, can not buy")
        return False
    if ask_data["failed"] is not None:
        print("Can't buy a failed ask.")
        return False    
    if ask_data["cancel_trx"] is not None:
        print("Can't buy a cancelled ask.")
        return False      
    if ask_data["buy_trx"] is not None:
        print("Can't buy a already filled ask.")
        return False
    if market == user:
        print("The Market can't be a buyer")
        return False

    # Check availability of goods
    # ITEM
    if category == "item":
        table = connection["items"]
        item = table.find_one(uid=uid)  
        if item is None:
            print("Item %s does not exist" % uid)
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["items"]
            table.update({"uid":uid, "for_sale": 0}, ["uid"])
            return False    
        if seller == user:
            print("You can't buy your own items.")
            return False                        
        if item["activated_to"] is not None:
            print("You can't buy activated items")
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["items"]
            table.update({"uid":uid, "for_sale": 0}, ["uid"])
            return False      
    # PLANET
    elif category == "planet":
        table = connection["planets"]
        planet = table.find_one(id=uid) 
        if planet is None:
            print("Planet %s does not exist" % uid)
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["planets"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
        if planet["user"] == user:
            print("You can't buy your own planets")
            return False  
        if planet["startplanet"] == 1:
            print("You can't buy a start planet")
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["planets"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
        
        # Check outgoing missions
        cords_hor = planet["cords_hor"]
        cords_ver = planet["cords_ver"]       
        table = connection["missions"]
        missions_list = []
        for row in table.find(user=user, cords_hor=cords_hor, cords_ver=cords_ver, order_by='-busy_until'):
            if row['busy_until_return'] is not None and row['busy_until_return'] < time_now:
                continue
            elif row['busy_until_return'] is None and row['busy_until'] < time_now:
                continue        
            missions_list.append(row)   
        if len(missions_list) > 0:
            print("Could not buy planet %s, %d missions are active" % (uid, len(missions_list)))
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["planets"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
    # SHIP
    elif category == "ship":
        planet_id = None
        planet_hor = None
        planet_ver = None
        table = connection["ships"]
        ship = table.find_one(id=uid) 
        if ship is None:
            print("Ship %s does not exist" % uid)
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False     
        if ship["user"] == user:
            print("You can't buy your own ships")
            return False   
        if (ship["busy_until"] > time_now):
            print("ship %s is still busy" % uid)
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
        if (ship["mission_busy_until"] > time_now):
            print("ship %s is on a mission" % uid)
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
        if planet_hor is None:
            planet_hor = ship["cords_hor"]
            planet_ver = ship["cords_ver"]
        elif planet_hor != ship["cords_hor"] or planet_ver != ship["cords_ver"]:
            print("Ship %d is not at %d/%d" %(shipid, planet_hor, planet_ver))
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False           
        if planet_hor is None:
            print("Could not find planet_id")
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False         
        planet_id = get_planetid (planet_hor, planet_ver)
        if planet_id is None:
            print("Could not find planet_id")
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False       
        table = connection["planets"]
        planet_from_data = table.find_one(id=planet_id)
        if planet_from_data is None:
            print("Could not find planet_id")
            table = connection["asks"]
            table.update({"id": ask_id, "buy_trx": trx_id, "failed": time_now}, ["id"])
            table = connection["ships"]
            table.update({"id":uid, "for_sale": 0}, ["id"])
            return False    
        cords_hor = planet_from_data["cords_hor"]
        cords_ver = planet_from_data["cords_ver"]    
    else:
        print("Not supported category: %s" % category)
        return False    

    # Check stardust
    price = ask_data["price"]
    fee_market = ask_data["fee_market"]
    fee_market = int(fee_market)
    fee_burn = ask_data["fee_burn"]
    fee_burn = int(fee_burn)
    cost_good = int(price - fee_market - fee_burn)

    table = connection["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        errormsg = ("User %s does not exists" % user)
        print(errormsg)
        return False
    if userdata["stardust"] is not None:
        stardust_balance = int(userdata["stardust"])
    else: 
        stardust_balance = 0 
  
    if stardust_balance < price:
        print("Not enough stardust")
        return False
    
    # Excecute Trade
    # ITEM
    if category == "item":
        table = connection["items"]
        table.update({"uid":uid, "last_owner": seller, "owner": user, "item_gifted_at": (time_now), "for_sale": 0}, ["uid"])
    # PLANET
    elif category == "planet":    
        # Update Yamato Ranking for transferred ships
        # Get current season            
        table_season = connection["season"]
        last_season = table_season.find_one(order_by="-end_date")
        if last_season is None or last_season["end_date"] < time_now:
            current_season = None
        else:
            current_season = last_season
        if current_season is not None:
            season_id = int(current_season["id"])
        else:
            season_id = None

        if season_id is not None:       
            # Get Seller reward
            table_ranking = connection['seasonranking']
            ranking = table_ranking.find_one(season_id=season_id,user=seller)
            if ranking is not None:
                old_sender_build_reward = int(ranking["build_reward"])
                old_sender_total_reward = int(ranking["total_reward"])
            else:
                old_sender_build_reward = 0
                old_sender_total_reward = 0

            table = connection["ships"]
            delta_build_reward = 0
            for ship in table.find(user=seller, cords_hor=cords_hor, cords_ver=cords_ver):
                shipid = ship["id"]
                shiptype = ship["type"]
                if shiptype[:6] == "yamato":
                    if shiptype[6:] is not None and shiptype[6:] != "":
                        shiptier = int(shiptype[6:])
                    else:
                        continue
                    # Loop through all tiers with stardust to sum up total reward to tranfer   
                    for tier in range(1, shiptier+1):   
                        current_shiptype = "yamato"+str(tier)             
                        build_costs = upgrade_costs[current_shiptype]['1']
                        if build_costs["stardust"] is not None:
                            delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                        else:
                            delta_build_reward = delta_build_reward + 0
            if delta_build_reward != 0:                
                new_sender_build_reward = old_sender_build_reward - delta_build_reward
                new_sender_total_reward = old_sender_total_reward - delta_build_reward               
                table_ranking.upsert({"season_id": season_id, "user": seller, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"])  
        # Transfer Planet
        print("Transfer sold planet: "+str(uid))
        table = connection["planets"]
        data = dict(id=uid,user=user,for_sale=0)
        table.update(data,['id'])
        # Transfer Ships on Planet
        table = connection["ships"]
        n_ships = table.count(user=seller, cords_hor=cords_hor, cords_ver=cords_ver)
        if n_ships > 0:
            print("Transfer sold ships: "+str(n_ships))
            connection.begin()
            for ship in table.find(user=seller, cords_hor=cords_hor, cords_ver=cords_ver):
                table.update({"id": ship["id"], "user": user}, ["id"])
            connection.commit()  
        # ranking
        update_ranking_user(seller, time_now)
        update_ranking_user(user, time_now)
    # SHIP
    elif category == "ship":
        table = connection["planets"]
        new_planet = table.find_one(user=user,startplanet=1)
        if new_planet is None:
            print("No planet to transfer ships to")
            return Falset
        new_cords_hor = new_planet["cords_hor"]
        new_cords_ver = new_planet["cords_ver"]

        # Update Yamato Ranking for transferred ships         
        table_season = connection["season"]
        last_season = table_season.find_one(order_by="-end_date")
        if last_season is None or last_season["end_date"] < time_now:
            current_season = None
        else:
            current_season = last_season
        if current_season is not None:
            season_id = int(current_season["id"])
        else:
            season_id = None

        if season_id is not None:       
            # Get Seller reward
            table_ranking = connection['seasonranking']
            ranking = table_ranking.find_one(season_id=season_id,user=seller)
            if ranking is not None:
                old_sender_build_reward = int(ranking["build_reward"])
                old_sender_total_reward = int(ranking["total_reward"])
            else:
                old_sender_build_reward = 0
                old_sender_total_reward = 0

            table = connection["ships"]
            delta_build_reward = 0
            for ship in table.find(id=uid, user=seller, cords_hor=cords_hor, cords_ver=cords_ver):
                shipid = ship["id"]
                shiptype = ship["type"]
                if shiptype[:6] == "yamato":
                    if shiptype[6:] is not None and shiptype[6:] != "":
                        shiptier = int(shiptype[6:])
                    else:
                        continue
                    # Loop through all tiers with stardust to sum up total reward to tranfer   
                    for tier in range(1, shiptier+1):   
                        current_shiptype = "yamato"+str(tier)             
                        build_costs = upgrade_costs[current_shiptype]['1']
                        if build_costs["stardust"] is not None:
                            delta_build_reward = delta_build_reward + int(build_costs["stardust"])
                        else:
                            delta_build_reward = delta_build_reward + 0
            if delta_build_reward != 0:                
                new_sender_build_reward = old_sender_build_reward - delta_build_reward
                new_sender_total_reward = old_sender_total_reward - delta_build_reward               
                table_ranking.upsert({"season_id": season_id, "user": seller, "last_update": time_now, "build_reward":new_sender_build_reward, "total_reward": new_sender_total_reward}, ["season_id", "user"]) 

        mission_busy_until = time_now + timedelta(0) # TODO add 8 hours (?) for ships to arrive after buying them
        table = connection["ships"]
        table.update({"id":uid, "user": user, "cords_hor": new_cords_hor, "cords_ver": new_cords_ver,
                    "qyt_copper": 0, "qyt_uranium": 0, "qyt_ore": 0, "qyt_coal": 0, "mission_busy_until": (mission_busy_until),"last_update": (time_now),
                    "for_sale": 0}, ["id"])
    else:
        print("Not supported category: %s" % category)
        return False   

    # Stardust Transfers
    connection.begin()
    try:
        # Buyer
        table = connection['users']
        ownerdata = table.find_one(username=user)
        if ownerdata["stardust"] is not None:
            stardust_balance = int(ownerdata["stardust"])
        else: 
            stardust_balance = 0
        fin_qty_stardust = int(stardust_balance) - int(price)  
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "trade", "tr_status": 1, "date": time_now, "from_user":user, "to_user":seller, "amount":cost_good}) 
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "market", "tr_status": 1, "date": time_now, "from_user":user, "to_user":market, "amount":fee_market})    
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "fee", "tr_status": 1, "date": time_now, "from_user":user, "amount":fee_burn})       
        # Seller
        table = connection['users']
        ownerdata = table.find_one(username=seller)
        if ownerdata["stardust"] is not None:
            stardust_balance = int(ownerdata["stardust"])
        else: 
            stardust_balance = 0
        fin_qty_stardust = int(stardust_balance) + int(cost_good)         
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])              
        # Market 
        table = connection['users']
        ownerdata = table.find_one(username=market)
        if ownerdata["stardust"] is not None:
            stardust_balance = int(ownerdata["stardust"])
        else: 
            stardust_balance = 0
        fin_qty_stardust = int(stardust_balance) + int(fee_market)   
        table = connection["users"]
        table.update({"id": ownerdata["id"], "stardust": fin_qty_stardust}, ["id"])     
        # Log Result
        table = connection["asks"]
        table.update({"id": ask_id, "buy_trx": trx_id, "sold": time_now}, ["id"])
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False      

    return True

def buff(user, buff, parameter, time_now, block_num, trx_id):
    connection = connectdb()
    # Get Buff 
    table = connection["buffs"]
    buffdata = table.find_one(name=buff)
    if buffdata is None:
        print("Buff does not exist")
        return False
    price = int(buffdata["price"])
    buff_duration = int(buffdata["buff_duration"])
    
    # Get User
    table = connection["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        print("User does not exist")
        return False
    buff_column = "b_"+str(buff)
    buff_from = userdata[buff_column]

    # Calculate new buff
    if buff_from is None:
        buff_from = time_now
    if buff_from < time_now:
        buff_from = time_now
    new_buff_end = buff_from + timedelta(days=buff_duration)

    # Calculate Stardust
    if userdata["stardust"] is not None:
        stardust_balance = int(userdata["stardust"])
    else: 
        stardust_balance = 0 
    fin_qty_stardust = int(stardust_balance) - int(price)   

    if fin_qty_stardust < 0:
        print("Not enough stardust to buy buff")
        return False

    # Write to DB 
    connection.begin()
    try:
        table = connection["users"]
        table.update({"id": userdata["id"], "stardust": fin_qty_stardust, buff_column: new_buff_end}, ["id"])
        table = connection["stardust"]
        table.insert({"trx": trx_id, "tr_type": "buff", "tr_status": 1, "date": time_now, "from_user":user, "amount":price})      
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False

    return True

def updatebuff(buff, price, time_now, block_num, trx_id):
    connection = connectdb()
    table = connection["buffs"]
    buffdata = table.find_one(name=buff)
    if buffdata is None:
        print("Buff not found")
        return False
    
    try:
        price = float(price)
    except:
        print("Could not parse price")
        return False
    int_price = int(price * 1e8)

    connection.begin()
    try:
        table = connection["buffs"]
        table.update({"id": buffdata["id"], "price": int_price}, ["id"])    
        connection.commit()
    except:
        connection.rollback()
        print ("Database transaction failed")
        return False     

    return True

def buy(command, amount, time_now, block_num, trx_id, transfer_id):
    connection = connectdb()
    table = connection["shop"]
    shopitem = table.find_one(itemid=command["itemid"])
    if shopitem is None:
        print("Shop item could not be found %s" % command["itemid"])
        update_transfer_status(False, transfer_id)
        return False
    
    try:
        qty = int(command["qty"])
    except:
        print("Wrong amount")
        update_transfer_status(False, transfer_id)
        return False
    price = float(shopitem["price"])
   
    if float(amount) < qty * price:
        print("Wrong amount")
        update_transfer_status(False, transfer_id)
        return False    
    table = connection["items"]
    n_items_bought = table.count(itemid=command["itemid"])
    n_items_bought_last_24h = table.count(itemid=command["itemid"], date={'>': time_now - timedelta(1)})
    print("%d items have been sold" % n_items_bought_last_24h)
    sales_per_day = shopitem["sales_per_day"]
    if command["itemid"] == "chest_01" and time_now <= datetime(2019,4,24,9,3,18):
        sales_per_day = 100
    elif command["itemid"] == "chest_01" and time_now > datetime(2019,4,24,9,3,18) and time_now < datetime(2019,4,27,22,0,0):
        sales_per_day = 150
    elif command["itemid"] == "chest_02" and time_now <= datetime(2019,4,25,6,49,0):
        sales_per_day = 50
    elif command["itemid"] == "chest_02" and time_now > datetime(2019,4,25,6,49,0) and time_now < datetime(2019,4,27,22,0,0):
        sales_per_day = 40   
    elif command["itemid"] == "chest_03" and time_now <= datetime(2019,4,25, 21,42,0):
        sales_per_day = 30
    elif command["itemid"] == "chest_03" and time_now > datetime(2019,4,25,21,42,0) and time_now < datetime(2019,4,27,22,0,0):
        sales_per_day = 25
    if sales_per_day > 0 and n_items_bought_last_24h + qty > sales_per_day:
        errormsg = ("Please wait %d/%d" % (n_items_bought_last_24h, sales_per_day))
        print(errormsg)
        update_transfer_status(False, transfer_id, errormsg)
        return False
    if shopitem["max_supply"] is not None and n_items_bought >= shopitem["max_supply"]:
        errormsg = ("Maximum supply of %d items is reached." % shopitem["max_supply"])
        print(errormsg)
        update_transfer_status(False, transfer_id, errormsg)
        return False
    elif shopitem["max_supply"] is not None:
        print("%d/%d sold" % (n_items_bought, shopitem["max_supply"]))
    table = connection["users"]
    userdata = table.find_one(username=command["user"])
    if userdata is None and trx_id not in ["2d4093016a191a0aa45fc3cade0a9cd38c69905c", "b24042cb476800bed04bb0191d22cf1bd7aa30c1",
                                           "cde299964c433ba17cb82274f296be07e5d5e561", "6e649476e4114f09ada1e92cc096b767cb57e2a7"]:
        errormsg = ("User %s does not exists" % command["user"])
        print(errormsg)
        update_transfer_status(False, transfer_id, errormsg)
        return False
    
    
    seed = get_seed(block_num, trx_id)   
    set_seed(seed)
    
    int_amount = int((float(amount) * 100) * 1e8)
    
    connection.begin()
    try:
        for i in range(qty):
            uid = uid_from_seed(shopitem["prefix"])
            table = connection["items"]
            table.insert({"uid": uid, "owner": command["user"], "date": time_now, "trx_id": trx_id, "block_num": block_num,
                          "itemid": command["itemid"]})
        table = connection["transfers"]
        table.update({"id": transfer_id, "tr_status": 1}, ["id"])
        
        if time_now <= datetime(2019,11,24,20,00,0):
            table = connection["users"]
            if userdata["stardust"] is None:
                table.update({"id": userdata["id"], "stardust": int_amount }, ["id"])
            else:
                table.update({"id": userdata["id"], "stardust": userdata["stardust"] + int_amount }, ["id"]) 
            table = connection["stardust"]
            table.insert({"trx": trx_id, "tr_type": "shop", "tr_status": 1, "date": time_now, "to_user":command["user"], "amount":int_amount})
        
        connection.commit()
    except:
        connection.rollback() 
        print ("Database transaction failed")
        return False
    return True

def issue(itemid, quantity, target, time_now, block_num, trx_id):
    connection = connectdb()
    table = connection["shop"]
    shopitem = table.find_one(itemid=itemid)
    if shopitem is None:
        print("Shop item could not be found %s" % itemid)
        return False
    if not shopitem["issueable"]:
        print("Shop item cannot be issued.")
        return False        
    try:
        qty = int(quantity)
    except:
        print("Wrong amount")
        return False

    table = connection["users"]
    userdata = table.find_one(username=target)
    if userdata is None:
        errormsg = ("User %s does not exists" % target)
        print(errormsg)
        return False
    
    
    seed = get_seed(block_num, trx_id)   
    set_seed(seed)
    connection.begin()
    try:
        for i in range(qty):
            uid = uid_from_seed(shopitem["prefix"])
            table = connection["items"]
            table.insert({"uid": uid, "owner": target, "date": time_now, "trx_id": trx_id, "block_num": block_num,
                          "itemid": itemid})
        connection.commit()
    except:  
        connection.rollback() 
        print ("Database transaction failed")
        return False
    return True