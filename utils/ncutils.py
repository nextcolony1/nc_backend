from beem.block import Block, BlockHeader
import hashlib
import random
import base36
import json
from math import hypot
import math
from random import randint
import os
import dataset
from datetime import datetime, timedelta

def read_config(config_file):
    config_file = os.path.abspath(os.path.join(os.path.join( os.path.dirname(__file__) , '..'), config_file ) )
    if not os.path.isfile(config_file):
        raise Exception("config.json is missing!")
    else:
        with open(config_file) as json_data_file:
            config_data = json.load(json_data_file)
    return config_data

def connectdb():
    if 'config_data' not in globals():
        config_data = read_config('config.json')
    databaseConnector = config_data["databaseConnector"]
    db = dataset.connect(databaseConnector)
    return db

def get_custom_json_id():
    config_data = None
    if 'config_data' not in globals():
        config_data = read_config('config.json')
    if config_data is None:
        return "nextcolony"
    if "custom_json_id" not in config_data:
        return "nextcolony"
    custom_json_id = config_data["custom_json_id"]

    return custom_json_id

def get_transfer_id():
    if 'config_data' not in globals():
        config_data = read_config('config.json')
    if config_data is None:
        return "nc"
    if "transfer_id" not in config_data:
        return "nc"        
    transfer_id = config_data["transfer_id"]    

    return transfer_id

def generateUid(length):
    number = round((pow(36, length + 1) - random.random() * pow(36, length)))
    return base36.dumps(number).upper()

def set_seed(seed):
    random.seed(a=seed, version=2)

def get_random_range(start, end):
    return math.floor((random.random() * (end-start + 1)) + start)

def uid_from_seed(prefix):
    return prefix+generateUid(10)

def get_is_empty_space(find_prob = 0.01):
    return random.random() >= find_prob

def found_stardust(find_prob = 0.1):
    return random.random() <= find_prob

def found_blueprint(find_prob = 0.15):
    return random.random() <= find_prob

def get_random_blueprint():
    drop = random.random()
    if drop <= 0.0023:
        blueprint = "blueprint_24" # dreadnought2 0.23%
    elif drop <= 0.0070:
        blueprint = "blueprint_23" # carrier2 0.47%
    elif drop <= 0.0164:
        blueprint = "blueprint_10" # transportship2 0.94%
    elif drop <= 0.0257:
        blueprint = "blueprint_22" # battlecruiser2 0.94%
    elif drop <= 0.0444:
        blueprint = "blueprint_21" # cruiser2 1.87%
    elif drop <= 0.0795:
        blueprint = "blueprint_20" # destroyer2 3.51%
    elif drop <= 0.1525:
        blueprint = "blueprint_19" # frigate2 7.31%
    elif drop <= 0.2987:
        blueprint = "blueprint_18" # corvette2 14.61%
    elif drop <= 0.4740:
        blueprint = "blueprint_17" # cutter2 17.53%
    elif drop <= 0.7078:
        blueprint = "blueprint_16" # patrol2 23.38%
    else:
        blueprint = "blueprint_15" # scout2 29.22%
    
    return blueprint

def get_burn_income(bonus, planet_type):
    income = 0
    if bonus == 4: # Legendary
        if planet_type == 5: # Uranium
            income = 9000000 * 1e8        
        elif planet_type == 4: # Copper
            income = 7000000 * 1e8
        elif planet_type == 3: # Ore
            income = 6000000 * 1e8
        elif planet_type == 2: # Coal
            income = 5000000 * 1e8
        else: # planet_type == "1": Atmosphere
            income = 3000000 * 1e8
    elif bonus == 3: # Rare
        if planet_type == 5: # Uranium
            income = 90000 * 1e8        
        elif planet_type == 4: # Copper
            income = 70000 * 1e8
        elif planet_type == 3: # Ore
            income = 60000 * 1e8
        elif planet_type == 2: # Coal
            income = 50000 * 1e8
        else: # planet_type == "1": Atmosphere
            income = 30000 * 1e8
    elif bonus == 2: # Uncommon  
        if planet_type == 5: # Uranium
            income = 30000 * 1e8        
        elif planet_type == 4: # Copper
            income = 25000 * 1e8
        elif planet_type == 3: # Ore
            income = 20000 * 1e8
        elif planet_type == 2: # Coal
            income = 18000 * 1e8
        else: # planet_type == "1": Atmosphere
            income = 10000 * 1e8
    else: # bonus == "1" Common 
        if planet_type == 5: # Uranium
            income = 15000 * 1e8        
        elif planet_type == 4: # Copper
            income = 12000 * 1e8
        elif planet_type == 3: # Ore
            income = 10000 * 1e8
        elif planet_type == 2: # Coal
            income = 9000 * 1e8
        else: # planet_type == "1": Atmosphere
            income = 5000 * 1e8

    return income

def get_random_stardust(from_amount, to_amount):
    return randint(from_amount,to_amount)

def get_explorer_not_broke():
    return random.random() >= 0.05

def get_random_bonus():
    planet_bonus_seed = random.random()
    bonus = 1
    if planet_bonus_seed >= 0.4:
        bonus = 1 # 60%
    elif planet_bonus_seed >= 0.1:
        bonus = 2 # 30%
    elif planet_bonus_seed >= 0.00001:
        bonus = 3 # 9.999 %
    else:
        bonus = 4 # 0.001 %
    return bonus

def get_random_type_old():
    planet_type_seed = random.random()
    if planet_type_seed >= 0.35:
        type = 2
    elif planet_type_seed >= 0.55:
        type = 3
    elif planet_type_seed >= 0.73:
        type = 4
    elif planet_type_seed >= 0.88:
        type = 5
    else:
        type = 1 
    return type

def get_random_type():
    planet_type_seed = random.random()
    if planet_type_seed >= 0.88:
        type = 5 # 12%    
    elif planet_type_seed >= 0.73:
        type = 4 # 15%       
    elif planet_type_seed >= 0.55:
        type = 3 #18%       
    elif planet_type_seed >= 0.35:
        type = 2 # 20%
    else:
        type = 1 # 35%
    return type

def get_random_img(max_img_number):
    return get_random_range(1, max_img_number)

def read_parameter():
    parameter = {}
    upgrade_costs = {}
    upgrade_keys = ["shipyard", "oredepot", "copperdepot", "coaldepot", "uraniumdepot", "explorership",
                    "transportship", "scout", "patrol", "cutter", "corvette", "frigate", "destroyer", "cruiser", "battlecruiser",
                    "carrier", "dreadnought","yamato", "yamato1", "yamato2", "yamato3","yamato4","yamato5","yamato6","yamato7","yamato8","yamato9","yamato10","yamato11","yamato12",
                      "yamato13","yamato14","yamato15","yamato16","yamato17","yamato18","yamato19","yamato20", "oremine", "coppermine", "coalmine", "uraniummine", "base", "researchcenter",
                    "bunker", "shieldgenerator"]
    
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
                    "Carrier", "Dreadnought", "Yamato","oremine", "coppermine", "coalmine", "uraniummine", "base", "researchcenter",
                    "orebooster", "coalbooster", "copperbooster", "uraniumbooster", "missioncontrol", "bunker",                   
                    "enlargebunker", "structureimprove", "armorimprove", "shieldimprove",
                    "rocketimprove", "bulletimprove", "laserimprove", "regenerationbonus", "repairbonus",
                    "shieldgenerator" ]
    
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
    connection.executable.close()
    return parameter


def coords_to_solarsystem(x,y):
    if abs(x) <=  5:
        x_solarsystem = 0
    elif x > 0:
        x_solarsystem = math.ceil((x - 5) / 11)
    else:
        x_solarsystem = math.floor((x + 5) / 11)
    if abs(y) <= 5:
        y_solarsystem = 0
    elif y > 0:
        y_solarsystem = math.ceil((y - 5) / 11)
    else:
        y_solarsystem = math.floor((y + 5) / 11)
    return (x_solarsystem, y_solarsystem)

def coords_to_region(x,y):
    x_solarsystem, y_solarsystem = coords_to_solarsystem(x,y)
    x_region, y_region = coords_to_solarsystem(x_solarsystem,y_solarsystem)
    return x_region, y_region

def coords_to_galaxy(x,y):
    x_solarsystem, y_solarsystem = coords_to_solarsystem(x,y)
    x_region, y_region = coords_to_solarsystem(x_solarsystem,y_solarsystem)
    x_galaxy, y_galaxy = coords_to_solarsystem(x_region,y_region)
    return x_galaxy, y_galaxy

def coords_to_deepspace(x,y):
    x_solarsystem, y_solarsystem = coords_to_solarsystem(x,y)
    x_region, y_region = coords_to_solarsystem(x_solarsystem,y_solarsystem)
    x_galaxy, y_galaxy = coords_to_solarsystem(x_region,y_region)
    x_deepspace, y_deepspace = coords_to_solarsystem(x_galaxy,y_galaxy)
    return x_deepspace, y_deepspace

def galaxy_to_donut(x_galaxy, y_galaxy):
    return max(abs(x_galaxy), abs(y_galaxy))

def galaxy_to_coords(x_galaxy, y_galaxy):
    x_region, y_region = solarsystem_to_coords(x_galaxy,y_galaxy)
    x_solarsystem,y_solarsystem = solarsystem_to_coords(x_region,y_region)
    x,y = solarsystem_to_coords(x_solarsystem,y_solarsystem)
    return x,y

def coords_to_donut(x, y):
    x_galaxy, y_galaxy = coords_to_region(x,y)
    return max(abs(x_galaxy), abs(y_galaxy)) + 1

def get_free_solarsystem_in_donat(coords_list, solarsystem_list, region_list, galaxy_x, galaxy_y, d, add_legendary=False):
    connection = connectdb()
    offset_x, offset_y = galaxy_to_coords(galaxy_x, galaxy_y)
    region_offset_x, region_offset_y = coords_to_region(offset_x, offset_y)
    table = connection['planets']
    
    free_region_found = False
    free_solarsystem_found = False
    try_list = []
    n = get_donut_regions(d)
    while not free_region_found:
        
        x_region, y_region = get_random_region_in_donut(d)
        x_region += region_offset_x
        y_region += region_offset_y
        # print("donut %d, x,y: %d, %d" % (d, x_region, y_region))
        if add_legendary and (x_region, y_region) in region_list:
            continue
        if (x_region, y_region) not in try_list:
            try_list.append((x_region, y_region))
        xy_list = []
        while len(xy_list) < 121:
            x_solarsystem, y_solarsystem = get_random_solarsystem_in_region(x_region, y_region)
            
            if (x_solarsystem, y_solarsystem) not in solarsystem_list:
                return x_solarsystem, y_solarsystem
            if (x_solarsystem, y_solarsystem) not in xy_list:
                xy_list.append((x_solarsystem, y_solarsystem))
        if len(try_list) == n:
            return None, None
        

def get_random_region_in_donut(d):
    if d == 1:
        return 0,0
    n = get_donut_regions(d)
    x_region = 0
    y_region = 0
    selected_region = get_random_range(1,n)
    return selected_donat_region_to_coords(d, selected_region)

def get_random_solarsystem_in_region(x_region,y_region):
    x = get_random_range(-5,5)
    y = get_random_range(-5,5)
    x_center, y_center = solarsystem_to_coords(x_region, y_region)
    return x+x_center, y+y_center

def get_random_coords_in_solarsystem(x_solarsystem,y_solarsystem):
    x = get_random_range(-5,5)
    y = get_random_range(-5,5)
    x_center, y_center = solarsystem_to_coords(x_solarsystem, y_solarsystem)
    return x+x_center, y+y_center

def selected_donat_region_to_coords(d, selected_region):
    n = get_donut_regions(d)
    long_side = 2*d -1
    short_side = 2*d -3
    if selected_region/n <= (n/4+1) /n:
        x_region = -d + 1
        y_region = selected_region - d
    elif selected_region/n <= 0.5:
        y_region = d - 1
        x_region =  (selected_region - (long_side) ) -d + 1
    elif selected_region/n <= (n/4+1) /n + 0.5:
        x_region = d - 1
        y_region =  -(selected_region - (long_side) - short_side) +d
    else:
        y_region = -d + 1
        x_region =  -(selected_region - (2*long_side) - short_side) +d -1
        
    return int(x_region), int(y_region)

def region_to_coords(x_region, y_region):
    x_solarsystem,y_solarsystem = solarsystem_to_coords(x_region, y_region)
    return solarsystem_to_coords(x_solarsystem,y_solarsystem)

def solarsystem_to_coords(x_solarsystem,y_solarsystem):
    x=0
    y=0
    if abs(x_solarsystem) <=  0:
        x = 0
    elif x_solarsystem > 0:
        x = (x_solarsystem * 11) 
    else:
        x = (x_solarsystem * 11) 
    if abs(y_solarsystem) <=  0:
        y = 0
    elif y_solarsystem > 0:
        y = (y_solarsystem * 11) 
    else:
        y = (y_solarsystem * 11) 
    return (x, y)


def get_donut_regions(d):
    if d == 1:
        return 1
    return 4 * (d * 2 - 2)


def uid_from_block(trx_id, block_num, qty, prefix):
    block = Block(block_num)
    seed = hashlib.md5((trx_id + block["block_id"] + block["previous"]).encode()).hexdigest()
    random.seed(a=seed, version=2)
    uid_list = []
    for i in range(qty):
        uid = prefix+generateUid(10)
        uid_list.append(uid)
    return uid_list

def get_building_parameter(building):
    if building == "oremine" or building == "ore":
        building_level = "level_ore"
        busy_parameter = "ore_busy"
        skill_name = "r_oremine"
    elif building == "coalmine" or building == "coal":
        building_level = "level_coal"
        busy_parameter = "coal_busy"
        skill_name = "r_coalmine"
    elif building == "coppermine" or building == "copper":
        building_level = "level_copper"
        busy_parameter = "copper_busy"
        skill_name = "r_coppermine"
    elif building == "uraniummine" or building == "uranium":
        building_level = "level_uranium"
        busy_parameter = "uranium_busy"
        skill_name = "r_uraniummine"
    elif building == "base":
        building_level = "level_base"
        busy_parameter = "base_busy"
        skill_name = "r_base"
    elif building == "researchcenter":
        building_level = "level_research"
        busy_parameter = "research_busy"
        skill_name = "r_researchcenter"
    elif building == "shipyard":
        building_level = "level_shipyard"
        busy_parameter = "shipyard_busy"
        skill_name = "r_shipyard"
    elif building == "oredepot":
        building_level = "level_oredepot"
        busy_parameter = "oredepot_busy"
        skill_name = "r_oredepot"
    elif building == "coaldepot":
        building_level = "level_coaldepot"
        busy_parameter = "coaldepot_busy"
        skill_name = "r_coaldepot"
    elif building == "copperdepot":
        building_level = "level_copperdepot"
        busy_parameter = "copperdepot_busy"
        skill_name = "r_copperdepot"
    elif building == "uraniumdepot":
        building_level = "level_uraniumdepot"
        busy_parameter = "uraniumdepot_busy"
        skill_name = "r_uraniumdepot"
    elif building == "bunker":
        building_level = "level_bunker"
        busy_parameter = "bunker_busy"
        skill_name = "r_bunker"
    elif building == "shieldgenerator":
        building_level = "level_shieldgenerator"
        busy_parameter = "shieldgenerator_busy"
        skill_name = "r_shieldgenerator"        
    else:
        building_level = None
        busy_parameter = None
        skill_name = None
    return (building_level, busy_parameter, skill_name)
    

def write_spacedb(c_hor,c_ver,user, time_now, block_num, trx_id, uid=None):
    connection = connectdb()
    table = connection['space']
    if uid is None:
        
        table.insert({"user": user, "date": time_now, "c_hor": c_hor, "c_ver": c_ver,
                      "trx_id": trx_id, "block_num": block_num})
    else:
        table.insert({"user": user, "date": time_now, "c_hor": c_hor, "c_ver": c_ver,
                      "trx_id": trx_id, "block_num": block_num, "planet_id": uid})        


def create_planet(x,y, uid, time_now, block_num, trx_id):
    print ("creating a new planet")
    connection = connectdb()
    table = connection['planets']
    table.insert({"id": uid, "img_id": 0, "name": 0, "bonus": 0, "planet_type": 0, "user": 0, "qyt_uranium": 0, 
                  "qyt_ore": 0, "qyt_copper": 0, "qyt_coal": 0, "level_uranium": 0, "level_ore": 0,
                  "level_copper": 0, "level_coal": 0, "level_ship": 0, "ship_current": 0, "level_base": 0,
                  "level_research": 0, "level_coaldepot": 0, "level_oredepot": 0, "level_copperdepot": 0,
                  "level_uraniumdepot": 0, "level_shipyard": 0, "ore_busy": time_now, "copper_busy": time_now,
                  "coal_busy": time_now, "uranium_busy": time_now, "research_busy": time_now, "base_busy": time_now,
                  "shipyard_busy": time_now, "oredepot_busy": time_now, "coaldepot_busy": time_now, "copperdepot_busy": time_now,
                  "uraniumdepot_busy": time_now, "last_update": time_now, "date_disc": time_now, "cords_hor": x, "cords_ver": y,
                  "block_num": block_num, "trx_id": trx_id})

def get_planetid (c_hor,c_ver):
    connection = connectdb()
    table = connection["planets"]     
    result = table.find_one(cords_hor=c_hor, cords_ver=c_ver)
    if result is None:
        return(None)
    else:
        #print (result)
        planetid = result['id']
        return (planetid)

def get_distance (c_hor1,c_ver1,c_hor2,c_ver2):

    return (hypot(c_hor2-c_hor1,c_ver2-c_ver1))

def get_flight_param(shipstats,distance,apply_battlespeed = False):
    # calculate the time until arrival
    speed = shipstats['speed']
    if apply_battlespeed:
        speed = shipstats["battlespeed"]
    flight_duration = float(distance) / float(speed)
    #calculate the use of uranium
    consumption = shipstats['consumption']
    uranium_consumption = float(distance) * float(consumption)
    uranium_consumption = int(uranium_consumption * 1e5) / 1e5
    return (uranium_consumption, flight_duration)

def shipdata(shipid):
    connection = connectdb()
    table = connection["ships"]
    result = table.find_one(id=shipid)
    return result


def get_shipdata(shipid):
    connection = connectdb()
    table = connection["ships"]
    result = table.find_one(id=shipid)    
    if result is None:
        return None
    else:
        type = result['type']
        level = result['level']
        user = result['user']
        cords_hor = result['cords_hor']
        cords_ver = result['cords_ver']
        qty_copper = result['qyt_copper']
        qty_uranium = result['qyt_uranium']
        qty_coal = result['qyt_coal']
        qty_ore = result['qyt_ore']
        busy_until = result['busy_until']
        mission_id = result['mission_id']
        home_planet_id = result['home_planet_id']
        return (type,level,user,cords_hor,cords_ver,qty_copper,qty_uranium,qty_coal,qty_ore,busy_until, mission_id, home_planet_id)

def get_mission_data(id,var):
    # Connect to the database
    try:
        connection = connectdb()
        table=connection["missions"]
        results = table.find_one(mission_id=id)    
        
        if results is None:
            return None                
        #print(results)
        data = results[str(var)]
        connection.executable.close()
        return(data)
    except:
        return None
    finally:
        connection.executable.close()    

def get_ask_data(id,var):
    # Connect to the database
    try:
        connection = connectdb()
        table=connection["asks"]
        results = table.find_one(id=id)    
        
        if results is None:
            return None                
        #print(results)
        data = results[str(var)]
        connection.executable.close()
        return(data)
    except:
        return None
    finally:
        connection.executable.close()    

def get_ship_data(id,var):
    # Connect to the database
    try:
        connection = connectdb()
        table=connection["ships"]
        results = table.find_one(id=id)    
        
        if results is None:
            return None                
        #print(results)
        data = results[str(var)]
        connection.executable.close()
        return(data)
    except:
        return None
    finally:
        connection.executable.close()


def get_item_data(uid,var):
    # Connect to the database
    try:
        connection = connectdb()
        table=connection["items"]
        results = table.find_one(uid=uid)    
        
        if results is None:
            return None                
        #print(results)
        data = results[str(var)]
        connection.executable.close()
        return(data)
    except:
        return None
    finally:
        connection.executable.close()

def get_planet_data(id,var):
    # get the productivity data from the SQL DB
    # Connect to the database
    try:
        connection = connectdb()
        table = connection["planets"]
        results = table.find_one(id=id)    
        if results is None:
            return None       
        data = results[str(var)]
        return(data)
    except:
        return None
    finally:
        connection.executable.close()  

def update_transaction_status(success, id, error=None):
    connection = connectdb()
    table = connection["transactions"]
    if success:
        tr_status = 1
    else:
        tr_status = 2
    if error is None:
        table.update({"id": id, "tr_status": tr_status}, ["id"])
    else:
        table.update({"id": id, "tr_status": tr_status, "error": error[:256]}, ["id"])
    connection.executable.close()   

def update_transfer_status(success, id, error=None):
    connection = connectdb()
    table = connection["transfers"]
    if success:
        tr_status = 1
    else:
        tr_status = 2
    if error is None:
        table.update({"id": id, "tr_status": tr_status}, ["id"])
    else:
        table.update({"id": id, "tr_status": tr_status, "error": error[:256]}, ["id"])    
    connection.executable.close()       

def get_planetdata(planetid):
    connection = connectdb()
    table = connection["planets"]
    result = table.find_one(id=planetid)     
    if result is None:
        return None
    else:
        print (result)
        id = result['id']
        name = result['name']
        bonus = result['bonus']
        planet_type = result['planet_type']
        user = result['user']
        cords_hor = result['cords_hor']
        cords_ver = result['cords_ver']
        qty_copper = result['qyt_copper']
        qty_uranium = result['qyt_uranium']
        qty_coal = result['qyt_coal']
        qty_ore = result['qyt_ore']
        level_uranium = result['level_uranium']
        level_copper = result['level_copper']
        level_coal = result['level_coal']
        level_ore = result['level_ore']
        level_ship = result['level_ship']
        level_base = result['level_base']
        level_research = result['level_research']
        level_coaldepot = result['level_coaldepot']
        level_oredepot = result['level_oredepot']
        level_uraniumdepot = result['level_uraniumdepot']
        level_copperdepot = result['level_copperdepot']
        level_shipyard = result['level_shipyard']
        ore_busy = result['ore_busy']
        copper_busy = result['copper_busy']
        coal_busy = result['coal_busy']
        uranium_busy = result['uranium_busy']
        research_busy = result['research_busy']
        base_busy = result['base_busy']
        shipyard_busy = result['shipyard_busy']
        oredepot_busy = result['oredepot_busy']
        copperdepot_busy = result['copperdepot_busy']
        coaldepot_busy = result['coaldepot_busy']
        uraniumdepot_busy = result['uraniumdepot_busy']
        last_update = result['last_update']

        return (id,name,bonus,planet_type,user,cords_hor,cords_ver,qty_copper,qty_uranium,qty_coal,qty_ore,level_uranium,level_copper,level_coal,level_ore,level_ship,\
                level_base,level_research,level_coaldepot,level_oredepot,level_uraniumdepot,level_copperdepot,level_shipyard,ore_busy,copper_busy,coal_busy,uranium_busy,\
                research_busy,base_busy,shipyard_busy,oredepot_busy,copperdepot_busy,coaldepot_busy,uraniumdepot_busy,last_update)


def explore_planet(uid, owner, type, bonuslevel, img_id, time_now):

    init_lvl_copper = 0
    init_lvl_coal = 0
    init_lvl_ore = 0
    init_lvl_uranium = 0
    init_lvl_base = 1
    init_qty_copper = 0
    init_qty_coal = 0
    init_qty_ore = 0
    init_qty_uranium = 0
    next_planet_name = {0: "Alpha", 1: "Beta", 2: "Gamma", 3:"Delta", 4: "Epsilon", 5: "Zeta", 6: "Eta",
                        7: "Theta", 8: "Iota", 9: "Kappa", 10: "Lambda", 11: "Mu", 12: "Nu", 13: "Xi",
                        14: "Omicron", 15: "Pi", 16: "Rho", 17: "Sigma", 18: "Tau", 19: "Upsilon",
                        20: "Phi", 21: "Chi", 22: "Psi", 23: "Omega"}
    
    connection = connectdb()
    table = connection["planets"]
    n_planets = table.count(user=owner)
    planet_count = table.count(user=owner)
    planetdata = table.find_one(id=uid)
    if planetdata is None:
        return (False)
    else:
        table = connection["planets"]
        if n_planets > 23:
            n_planets = 23
        elif n_planets < 0:
            n_planets = 0
        user = planetdata['user']

        if planet_count <= 23:
            next_name = next_planet_name[n_planets]
        else:
            next_name = "Apeiron-"+str(planet_count)

        if user == "0":

            connection = connectdb()
            table = connection["planets"]
            table.update({"name": next_name, "user": owner, "planet_type": type, "img_id": img_id,
                          "bonus": bonuslevel, "qyt_uranium": init_qty_uranium, "level_base": init_lvl_base,
                          "qyt_ore": init_qty_ore, "qyt_copper": init_qty_copper, "qyt_coal": init_qty_coal,
                          "level_uranium": init_lvl_uranium, "level_ore": init_lvl_ore, "id": uid}, ["id"])        
            #enter the new data into the planets database
                # Read a single record


        return (True)


def find_starterplanet_coords(reg_h,reg_v):

    # find a spawn point - generate two random int mumbers in the range of 0 to 10 and substract 5 and than multiply with 11 - these are the mid points of the players starting solar system
    
    if int(reg_h)==0:
        reg_h = get_random_range(-5,5)
    if int(reg_v)==0:
        reg_v = get_random_range(-5,5)

    sp_h_add = get_random_range(-5,5)
    sp_h = int(int(reg_h)*121 +sp_h_add)
    print(sp_h)
    sp_v_add = get_random_range(-5,5)
    sp_v = int(int(reg_v)*121 +sp_v_add)
    print (sp_v)

    # check in the user db if the spawn points are already taken
    connection = connectdb()
    table = connection['users']
    sp_exist = table.find_one(sp_h=sp_h,sp_v=sp_v )

    # if not - find the final starting coordinates
    if not sp_exist:
        print ("Good solar system found")
        sp_h_add2 = get_random_range(-5,5)
        sp_h_final = sp_h + sp_h_add2
        sp_v_add2 = get_random_range(-5,5)     
        sp_v_final = sp_v + sp_v_add2
        # check if another plan exists already on these coordinates
        table = connection['planets']
        sp_exist = table.find_one(cords_hor=sp_h_final,cords_ver=sp_v_final)
        
        if not sp_exist:
            print (sp_h_final)
            print (sp_v_final)
            return(sp_h_final,sp_v_final)

def checkifuser(name):
    # Connect to the database
    connection = connectdb()
    table = connection["users"]    
    result = table.find_one(username=name)
    if result is None:
        return (False)
    else:
        return (True)

def findfreespot(time_now):
    print("Finding a free spot in the galaxy")
    success = False
    connection = connectdb()
    table = connection["planets"]
    while not success:
        x = randint(-100,100)
        y = randint(-100,100)
        # Connect to the database
        result = table.find_one(cords_hor=x, cords_ver=y)
        if result is None:
            print("no planet on this coordinates")
            success = True
        else:
            print(result["id"])
    return (x,y)

def findfreeplanet(time_now):
    success = False
    connection = connectdb()
    table = connection["planets"]    
    while not success:
        x = randint(-100,100)
        y = randint(-100,100)
        # Connect to the database
        result = table.find_one(cords_hor=x, cords_ver=y)
        if result is None:
            print("no planet on this coordinates")
        else:
                if result['user'] == '0':
                    success = True
                    print ("Free planet found with coordinates: "+str(x)+"," +str(y))
                else:
                    print ("Planet is already taken")

    return (x,y)
