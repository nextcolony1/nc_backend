import json
from datetime import timedelta, datetime
from beem.block import Block, BlockHeader
from beem.amount import Amount
from beem.nodelist import NodeList

from beem import Steem
import requests
import time
import requests
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
from utils.ncutils import find_starterplanet_coords, uid_from_block, write_spacedb, get_ship_data, get_item_data, get_planet_data, update_transaction_status, update_transfer_status
from utils.ncutils import set_seed, uid_from_seed, get_is_empty_space, get_random_bonus, get_random_type, get_planetid, explore_planet, get_random_img
from utils.ncutils import get_explorer_not_broke, get_free_solarsystem_in_donat, get_random_coords_in_solarsystem, coords_to_region, get_building_parameter
from utils.ncutils import coords_to_solarsystem
# get the productivity data from the SQL DB
# Connect to the database

def apply_damage(tank_stats, tank_index, shooter_stats, shooter_index, defender, leftOver, rates, shipstats, battle_round, time_now):
    
    
    shieldregreduce = 0.005
    if time_now < datetime(2019, 7, 12, 22, 0, 0):
        shieldregen = 0.2
        armorrep = 0.1
    else:
        shieldregen = 0
        armorrep = 0                
    armorregreduce = 0.01
    piercerateshield = 1
    pierceratearmor = 1    
    pierceratestructure = 1
    
    lolaser = 0
    lobullet = 0
    lorocket = 0
    
    lolaser2 = 0
    lobullet2 = 0
    lorocket2 = 0
    
    damageLaser = 0
    damageBullet = 0
    damageRocket = 0
    
    lOver = False
    
    if leftOver["laser"] > 0:
        damageLaser = leftOver["laser"]
        lOver = True
    else:
        damageLaser = shooter_stats[shooter_index]["laser"]
        
    if leftOver["bullet"] > 0:
        damageBullet = leftOver["bullet"]
        lOver = True
    else:
        damageBullet = shooter_stats[shooter_index]["bullet"]
        
    if leftOver["rocket"] > 0:
        damageRocket = leftOver["rocket"]
        lOver = True
    else:
        damageRocket = shooter_stats[shooter_index]["rocket"]
        
        
    
    
    if defender["r_rocketimprove"] is None:
        d_roi = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_roi = (1 + int(defender["r_rocketimprove"]) / 100)
    else:
        d_roi = 1 + (int(defender["r_rocketimprove"]) / 100)
        
    if defender["r_bulletimprove"] is None:
        d_bui = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_bui = (1 + int(defender["r_bulletimprove"]) / 100)
    else:
        d_bui = 1 + (int(defender["r_bulletimprove"]) / 100)               
    if defender["r_laserimprove"] is None:
        d_lai = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_lai = (1 + int(defender["r_laserimprove"]) / 100)
    else:
        d_lai = 1 + (int(defender["r_laserimprove"]) / 100)
        
    if defender["r_structureimprove"] is None:
        d_sti = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_sti = (1 + int(defender["r_structureimprove"]) / 100)
    else:
        d_sti = 1 + (int(defender["r_structureimprove"]) / 100)               
    if defender["r_armorimprove"] is None:
        d_ari = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_ari = (1 + int(defender["r_armorimprove"]) / 100)  
    else:
        d_ari = 1 + (int(defender["r_armorimprove"]) / 100)  
    if defender["r_shieldimprove"] is None:
        d_shi = 1
    elif time_now < datetime(2019, 7, 12, 22, 0, 0):
        d_shi = (1 + int(defender["r_shieldimprove"]) / 100) 
    else:
        d_shi = 1 + (int(defender["r_shieldimprove"]) / 100)     
    
    if time_now < datetime(2019, 7, 12, 22, 0, 0):
        if defender["r_regenerationbonus"] is None:
            shieldregen = 0.2
        else:
            shieldregen = (20 + int(defender["r_regenerationbonus"]) / 2) / 100
        if defender["r_repairbonus"] is None:
            armorrep = 0.1
        else:
            armorrep = (10 + int(defender["r_repairbonus"]) / 2) / 100
    else:
        if defender["r_regenerationbonus"] is None:
            shieldregen = 0
        else:
            shieldregen = int(defender["r_regenerationbonus"]) / 200
        if defender["r_repairbonus"] is None:
            armorrep = 0
        else:
            armorrep = int(defender["r_repairbonus"]) / 200                        
        
       
    if tank_stats[tank_index]["shield"] > 0:
        if (damageLaser * rates['laser']['shield'] > tank_stats[tank_index]["shield"]):
            lolaser = max((damageLaser * rates['laser']['shield'] - tank_stats[tank_index]["shield"]) / rates['laser']['shield'], 0) * piercerateshield
            if lOver:
                leftOver["laser"] = lolaser
        else:
            lolaser = 0
            if lOver:
                leftOver["laser"] = lolaser
                
        if (damageBullet  * rates['bullet']['shield'] > tank_stats[tank_index]["shield"]):
            lobullet = max((damageBullet * rates['bullet']['shield'] - tank_stats[tank_index]["shield"]) / rates['bullet']['shield'], 0) * piercerateshield
            if lOver:
                leftOver["bullet"] = lobullet            
        else:
            lobullet = 0     
            if lOver:
                leftOver["bullet"] = lobullet            
    
        if (damageRocket * rates['rocket']['shield'] > tank_stats[tank_index]["shield"]):
            lorocket = max((damageRocket * rates['rocket']['shield'] - tank_stats[tank_index]["shield"]) / rates['rocket']['shield'], 0) * piercerateshield
            if lOver:
                leftOver["rocket"] = lorocket             
        else:
            lorocket = 0
            if lOver:
                leftOver["rocket"] = lorocket     
                
        tank_stats[tank_index]["shield"] = max(tank_stats[tank_index]["shield"] - damageLaser * rates['laser']['shield'], 0)
        tank_stats[tank_index]["shield"] = max(tank_stats[tank_index]["shield"] - damageBullet * rates['bullet']['shield'], 0)
        tank_stats[tank_index]["shield"] = max(tank_stats[tank_index]["shield"] - damageRocket * rates['rocket']['shield'], 0)
        
        if tank_stats[tank_index]["shield"] == 0:
            if (lolaser > tank_stats[tank_index]["armor"]):
                lolaser2 = max((lolaser * rates['laser']['armor'] - tank_stats[tank_index]["armor"]) / rates['laser']['armor'], 0) * pierceratearmor
                if lOver:
                    leftOver["laser"] = lolaser2                  
            else:
                lolaser2 = 0
                if lOver:
                    leftOver["laser"] = lolaser2 
                    
            if (lobullet > tank_stats[tank_index]["armor"]):
                lobullet2 = max((lobullet * rates['bullet']['armor'] - tank_stats[tank_index]["armor"]) / rates['bullet']['armor'], 0) * pierceratearmor
                if lOver:
                    leftOver["bullet"] = lobullet2                
            else:
                lobullet2 = 0   
                if lOver:
                    leftOver["bullet"] = lobullet2     

            if (lorocket > tank_stats[tank_index]["armor"]):
                lorocket2 = max((lorocket * rates['rocket']['armor'] - tank_stats[tank_index]["armor"]) / rates['rocket']['armor'], 0) * pierceratearmor
                if lOver:
                    leftOver["rocket"] = lorocket2                  
            else:
                lorocket2 = 0               
                if lOver:
                    leftOver["rocket"] = lorocket2                  
            tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - lolaser * rates['laser']['armor'], 0)
            tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - lobullet * rates['bullet']['armor'], 0)
            tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - lorocket * rates['rocket']['armor'], 0)

            if tank_stats[tank_index]["armor"] == 0:
                if lolaser2 > tank_stats[tank_index]["structure"]:
                    leftOver["laser"] = max((((lolaser2 * rates['laser']['structure']) - tank_stats[tank_index]["structure"]) / rates['laser']['structure']), 0) * pierceratestructure
                else:
                    leftOver["laser"] = 0
                    
                if lobullet2 > tank_stats[tank_index]["structure"]:
                    leftOver["bullet"] = max((((lobullet2 * rates['bullet']['structure']) - tank_stats[tank_index]["structure"]) / rates['bullet']['structure']), 0) * pierceratestructure
                else:
                    leftOver["bullet"] = 0

                if lorocket2 > tank_stats[tank_index]["structure"]:
                    leftOver["rocket"] = max((((lorocket2 * rates['rocket']['structure']) - tank_stats[tank_index]["structure"]) / rates['rocket']['structure']), 0) * pierceratestructure
                else:
                    leftOver["rocket"] = 0                
                tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lolaser2 * rates['laser']['structure'], 0)
                tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lobullet2 * rates['bullet']['structure'], 0)
                tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lorocket2 * rates['rocket']['structure'], 0)
                
                
    elif tank_stats[tank_index]["armor"] > 0:
        if (damageLaser * rates['laser']['armor'] > tank_stats[tank_index]["armor"]):
            lolaser = max((damageLaser * rates['laser']['armor'] - tank_stats[tank_index]["armor"]) / rates['laser']['armor'], 0) * pierceratearmor
            if lOver:
                leftOver["laser"] = lolaser            
        else:
            lolaser = 0
            if lOver:
                leftOver["laser"] = lolaser            
        if (damageBullet * rates['bullet']['armor'] > tank_stats[tank_index]["armor"]):
            lobullet = max((damageBullet * rates['bullet']['armor'] - tank_stats[tank_index]["armor"]) / rates['bullet']['armor'], 0) * pierceratearmor
            if lOver:
                leftOver["bullet"] = lobullet            
        else:
            lobullet = 0   
            if lOver:
                leftOver["bullet"] = lobullet            
        if (damageRocket * rates['rocket']['armor'] > tank_stats[tank_index]["armor"]):
            lorocket = max((damageRocket * rates['rocket']['armor'] - tank_stats[tank_index]["armor"]) / rates['rocket']['armor'], 0) * pierceratearmor
            if lOver:
                leftOver["rocket"] = lorocket            
        else:
            lorocket = 0
            if lOver:
                leftOver["rocket"] = lorocket            

        tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - damageLaser * rates['laser']['armor'], 0)
        tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - damageBullet * rates['bullet']['armor'], 0)
        tank_stats[tank_index]["armor"] = max(tank_stats[tank_index]["armor"] - damageRocket * rates['rocket']['armor'], 0)

        if tank_stats[tank_index]["armor"] == 0:
            if lolaser > tank_stats[tank_index]["structure"]:
                leftOver["laser"] = max(((lolaser * rates['laser']['structure'] - tank_stats[tank_index]["structure"]) / rates['laser']['structure']), 0) * pierceratestructure
            else:
                leftOver["laser"] = 0
            if lobullet > tank_stats[tank_index]["structure"]:
                leftOver["bullet"] = max(((lobullet * rates['bullet']['structure'] - tank_stats[tank_index]["structure"]) / rates['bullet']['structure']), 0) * pierceratestructure
            else:
                leftOver["bullet"] = 0
            if lorocket > tank_stats[tank_index]["structure"]:
                leftOver["rocket"] = max(((lorocket * rates['rocket']['structure'] - tank_stats[tank_index]["structure"]) / rates['rocket']['structure']), 0) * pierceratestructure
            else:
                leftOver["rocket"] = 0                    
            tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lolaser * rates['laser']['structure'], 0)
            tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lobullet * rates['bullet']['structure'], 0)
            tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - lorocket * rates['rocket']['structure'], 0)
            
    elif tank_stats[tank_index]["structure"] > 0:
        if (damageLaser * rates['laser']['structure'] > tank_stats[tank_index]["structure"]):
            leftOver["laser"] = max((damageLaser * rates['laser']['structure'] - tank_stats[tank_index]["structure"]) / rates['laser']['structure'], 0) * pierceratestructure
        else:
            leftOver["laser"] = 0
         
        if (damageBullet * rates['bullet']['structure'] > tank_stats[tank_index]["structure"]):
            leftOver["bullet"] = max((damageBullet * rates['bullet']['structure'] - tank_stats[tank_index]["structure"]) / rates['bullet']['structure'], 0) * pierceratestructure
        else:
            leftOver["bullet"] = 0   
        if (damageRocket * rates['rocket']['structure'] > tank_stats[tank_index]["structure"]):
            leftOver["rocket"] = max((damageRocket * rates['rocket']['structure'] - tank_stats[tank_index]["structure"]) / rates['rocket']['structure'], 0) * pierceratestructure
        else:
            leftOver["rocket"] = 0
        
        
        
        tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - damageLaser * rates['laser']['structure'], 0)
        tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - damageBullet * rates['bullet']['structure'], 0)
        tank_stats[tank_index]["structure"] = max(tank_stats[tank_index]["structure"] - damageRocket * rates['rocket']['structure'], 0)


    st = shipstats[tank_stats[tank_index]["type"]]
    tank_stats[tank_index]["survivor"] = math.ceil(tank_stats[tank_index]["structure"] / (st["structure"] * d_sti))
    tank_stats[tank_index]["laser"] = tank_stats[tank_index]["survivor"] * st["laser"] * d_lai
    tank_stats[tank_index]["bullet"] = tank_stats[tank_index]["survivor"] * st["bullet"] * d_bui
    tank_stats[tank_index]["rocket"] = tank_stats[tank_index]["survivor"] * st["rocket"] * d_roi
    tank_stats[tank_index]["lost"] = tank_stats[tank_index]["n"] - tank_stats[tank_index]["survivor"]
    
    
    
    if tank_stats[tank_index]["armor"] > 0:
        tank_stats[tank_index]["armor"] = min(tank_stats[tank_index]["armor"] + st["armor"] * d_ari * max(armorrep - armorregreduce * battle_round, 0), st["armor"] * d_ari * tank_stats[tank_index]["survivor"])
        
    if tank_stats[tank_index]["shield"] > 0:
        tank_stats[tank_index]["shield"] = min(tank_stats[tank_index]["shield"] + st["shield"] * d_shi * max(shieldregen - shieldregreduce * battle_round, 0), st["shield"] * d_shi * tank_stats[tank_index]["survivor"])


    return tank_stats, leftOver

