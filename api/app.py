from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.contrib.fixers import ProxyFix
from collections import OrderedDict
import os
import ast
import json
import sys
from prettytable import PrettyTable
from datetime import datetime, timedelta, timezone
import pytz
import math
import random
import logging
import click
import dataset
import re
from beem import Steem
from steemengine.market import Wallet



config_file = 'config.json'
with open(config_file) as json_data_file:
    config_data = json.load(json_data_file)
    
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["2000000 per day", "120 per minute"]
)

CORS(app, supports_credentials=True)

databaseConnector = config_data["databaseConnector"]


upgrade_keys = ["shipyard", "oredepot", "copperdepot", "coaldepot", "uraniumdepot", "explorership",
                "transportship", "scout","patrol","cutter","corvette", "frigate", "destroyer", "cruiser", "battlecruiser",
                "carrier", "dreadnought","yamato", "yamato1", "yamato2", "yamato3","yamato4","yamato5","yamato6","yamato7","yamato8","yamato9","yamato10","yamato11","yamato12",
                      "yamato13","yamato14","yamato15","yamato16","yamato17","yamato18","yamato19","yamato20", "oremine", "coppermine", "coalmine", "uraniummine", "base",
                "researchcenter", "bunker", "shieldgenerator", "transportship1", "transportship2"]


skill_keys = ["shipyard", "oredepot", "copperdepot", "coaldepot", "uraniumdepot", "Explorer",
                "Transporter", "Scout", "Patrol", "Cutter", "Corvette", "Frigate", "Destroyer", "Cruiser", "Battlecruiser",
                "Carrier", "Dreadnought", "Yamato", "oremine", "coppermine", "coalmine", "uraniummine", "base", "researchcenter",
                "orebooster", "coalbooster", "copperbooster", "uraniumbooster", "missioncontrol", "bunker", "enlargebunker",
                "structureimprove", "armorimprove", "shieldimprove",
                "rocketimprove", "bulletimprove", "laserimprove", "regenerationbonus", "repairbonus", "shieldgenerator",
                "siegeprolongation", "depotincrease"]



def GetPlanetImg(rarity, type, id):
    img = ""
    #Rarity
    if rarity == "undefined" or rarity == "common":
        img = img + "co"
    
    if(rarity == "uncommon"):
        img = img + "un"
    
    if(rarity == "rare"):
        img = img + "rar"
    
    if(rarity == "legendary"):
        img = img + "leg"
    
    img = img + "_"
    if(type == "earth"):
        img = img + "atm"
    else:
        img = img + str(type)
    
    img = img + "_"
    if(id == 0):
        img = img + "1"
    else:
        img = img + str(id)
    
    img = img + ".png"
    return img
    

@app.route('/')
def main():
    return ""

# {"coal":71.3231,"ore":23.2371,"uranium":0.832567,"copper":2.7048,"coalrate":320,"orerate":120,"copperrate":40,"uraniumrate":20,"coaldepot":480,"oredepot":240,"copperdepot":60,"uraniumdepot":30,"lastUpdate":1555960626}
@app.route('/loadqyt', methods=['GET'])
def loadqyt():
    """
    Add a new rule
    """
    planetid = request.args.get('id', None)
    if planetid is None:
        return jsonify({"coal": 0, "ore": 0, "copper": 0, "uranium": 0, "lastUpdate": 99999999999999})
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    p = table.find_one(id=planetid)

    if p is None:
        return jsonify({"coal": 0, "ore": 0, "copper": 0, "uranium": 0, "lastUpdate": 99999999999999})
    return jsonify({"coal": float(p["qyt_coal"]), "ore": float(p["qyt_ore"]), "copper": float(p["qyt_copper"]),
                    "uranium": float(p["qyt_uranium"]), "coalrate": float(p["rate_coal"]), "orerate": float(p["rate_ore"]),
                    "copperrate": float(p["rate_copper"]), "uraniumrate": float(p["rate_uranium"]), "coaldepot": float(p["depot_coal"]),
                    "oredepot": float(p["depot_ore"]), "copperdepot": float(p["depot_copper"]), "uraniumdepot": float(p["depot_uranium"]),
                    "lastUpdate": int(p["last_update"].timestamp())})

@app.route('/loadbuildings', methods=['GET'])
def loadbuildings():
    planetid = request.args.get('id', None)
    if planetid is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    p = table.find_one(id=planetid)
    
    if p is None:
        return jsonify([])
    baseLevel = p["level_base"]
    user = p["user"]
    
    table = db["users"]
    u = table.find_one(username=user)
    
    if p["shieldprotection_busy"] is not None:
        shieldprotection_busy = int(p["shieldprotection_busy"].timestamp())
    else:
        shieldprotection_busy = 0
    if p["shieldcharge_busy"] is not None:
        shieldcharge_busy = int(p["shieldcharge_busy"].timestamp())
    else:
        shieldcharge_busy = 0
    shieldcharged = p["shieldcharged"]    
    
    table = db["upgradecosts"]
    buildings = []
    types = []
    for orig_name in upgrade_keys:
        name = orig_name

        ressource = None
        if name.find("mine") > -1:
            name = name.replace("mine", "")
            ressource = name
        elif name.find("depot") > -1:
            ressource = name.replace("depot", "")
            # ressource = name
        elif name.find("center") > -1:
            name = name.replace("center", "")
        
        if "level_" + name not in p:
            current = 0
            time_busy = False
            cur_skill = 0
            continue
        else:
            current = p["level_" + name]
            if current is None:
                current = 0
                time_busy = False
                cur_skill = 0
            if name + "_busy" in p and p[name + "_busy"] is not None:
                time_busy = int(p[name + "_busy"].timestamp())
            if "r_" + orig_name in u:
                cur_skill = u["r_" + orig_name]
            
        table = db["productivity"]
        rr = table.find_one(name=orig_name, level=current)
        rrd = table.find_one(name=orig_name, level=current + 1)
        if ressource is not None:
            cur_rate = rr[ressource]
            if rrd is not None:
                next_rate = rrd[ressource]
            else:
                next_rate = None
        else:
            cur_rate = None
            next_rate = None
        misc = None
        if orig_name == "shieldgenerator":
            misc = {"shieldprotection_busy": shieldprotection_busy, "shieldcharge_busy": shieldcharge_busy, "shieldcharged": shieldcharged}
        table = db["upgradecosts"]
        r = table.find_one(name=orig_name, level=current + 1)
        if r is not None:
            realTime = (100 - baseLevel) / 100 * r["upgrade_time"]
            
            buildings.append({"name": orig_name, "current": current, "coal": float(r["coal"]),
                              "ore": float(r["ore"]), "copper": float(r["copper"]), "uranium": float(r["uranium"]),
                              "research": 0, "skill": cur_skill, "cur_rate": cur_rate,
                              "next_rate": next_rate, "base": 0, "time": int(realTime), "busy": time_busy, "misc": misc})
        else:
            buildings.append({"name": orig_name, "current": current, "coal": 0,
                              "ore": 0, "copper": 0, "uranium": 0,
                              "research": 0, "skill": cur_skill, "cur_rate": cur_rate,
                              "next_rate": next_rate, "base": 0, "time": int(0), "busy": time_busy, "misc": misc})            
        
    return jsonify(buildings)


@app.route('/loaduser', methods=['GET'])
def loaduser():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    u = table.find_one(username=user)
    s = db.query("SELECT SUM(stardust) FROM users WHERE username != 'null'")
    for row in s:
        stardust_supply = int(row['SUM(stardust)']) 
    if u is None:
        return jsonify([])
    
       
    return jsonify({"username": u["username"], "date": int(u["date"].timestamp()), "stardust": u["stardust"], "supply": stardust_supply})

@app.route('/sd_balance', methods=['GET'])
def sd_balance():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
   
    try:
        wallet = Wallet(user)
        se_balance = float(wallet.get_token(symbol="STARDUST")['balance'])
        se_balance = se_balance *100000000
    except:
        se_balance = 0
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    u = table.find_one(username=user)
    s = db.query("SELECT SUM(stardust) FROM users WHERE username != 'null'")
    for row in s:
        stardust_supply = int(row['SUM(stardust)'])
    if u is None:
        return jsonify([])
    
       
    return jsonify({"username": u["username"], "date": int(u["date"].timestamp()), "stardust": u["stardust"], "se_stardust": int(se_balance), "supply": stardust_supply})




@app.route('/currentseason', methods=['GET'])
def currentseason():

    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["season"]
    last_season = table.find_one(order_by="-end_date")
    if last_season is None:
        return jsonify({})
    if last_season["end_date"] < datetime.utcnow():
        return jsonify({})
    
       
    return jsonify(last_season)


@app.route('/wallet', methods=['GET'])
def wallet():
    user = request.args.get('user', None)
    limit = request.args.get('limit', None)
    page = request.args.get('page', None)    
    if user is None:
        return jsonify([])
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = None     
    if page is not None:
        try:
            page = int(page)
        except:
            page = 0
    else:
        page = 0    
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    u = table.find_one(username=user)

    s = db.query("SELECT SUM(stardust) FROM users WHERE username != 'null'")
    for row in s:
        stardust_supply = int(row['SUM(stardust)']) 
    if u is None:
        return jsonify([])
    
    transactions = []
    table = db["stardust"]
    for row in table.find(from_user=user):
        row["date"] = int(row["date"].timestamp())
        transactions.append(row)
    for row in table.find(to_user=user):
        row["date"] = int(row["date"].timestamp())
        transactions.append(row)    
        
        
    transactions = sorted(transactions, key=lambda m: m["date"], reverse=True)

    if page is None and limit is not None:
        transactions = transactions[:limit]
    elif page is not None and limit is not None:
        if len(transactions) < limit * page:
            return jsonify([])
        if len(transactions) < limit * (page + 1):
            transactions = transactions[limit * page:]
        else:
            transactions = transactions[limit * page:limit * (page + 1)]              
       
    return jsonify({"username": u["username"], "date": int(u["date"].timestamp()),
                    "stardust": u["stardust"], "supply": stardust_supply,
                    "transactions": transactions})


@app.route('/wallet_ranking', methods=['GET'])
def wallet_ranking():
    limit = request.args.get('limit', 150)
    page = request.args.get('page', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 150     
    if page is not None:
        try:
            page = int(page)
        except:
            page = None      
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    
    s = db.query("SELECT SUM(stardust) FROM users WHERE username != 'null'")
    for row in s:
        stardust_supply = int(row['SUM(stardust)'])    
    
    if stardust_supply == 0:
        stardust_supply = 1

    table = db["users"]
    stack = []
        
    for row in table.find(order_by="-stardust", _limit=limit):
        if row["username"] == "null":
            continue
        if row["stardust"] is not None:
            row["stardust"] = int(row["stardust"])
        else:
            row["stardust"] = 0
        stack.append({"user": row["username"],
                      "stardust": row["stardust"],
                      "percentage": row["stardust"] / stardust_supply})
    return jsonify(stack)


@app.route('/loadtransaction', methods=['GET'])
def loadtransaction():
    trx_id = request.args.get('trx_id', None)
    if trx_id is None:
        return jsonify([])
    limit = 10
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["transactions"]
    trx_list = []
    for trx in table.find(trx=trx_id, _limit=limit):
        trx["date"] = int(trx["date"].timestamp())
        trx_list.append(trx)
  
    if len(trx_list) == 0:
        return jsonify([])
    
    return jsonify(trx_list)


@app.route('/loadskills', methods=['GET'])
def loadskills():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    u = table.find_one(username=user)
  
    if u is None:
        return jsonify([])
    
    table = db["skillcosts"]
    skills = []
    types = []
    for name in skill_keys:
        # name = row["name"]
        #if row["name"] in types:
        #    continue        
        current = u["r_" + name]
        if u["r_" + name + "_busy"] is None:
            time_busy = 0
        else:
            time_busy = int(u["r_" + name + "_busy"].timestamp())
        if current is None:
            
            current = 0
        table = db["skillcosts"]
        r = table.find_one(name=name, level=(current + 1))
            
        if r is not None:
            # types.append(row["name"])
            skills.append({"name": name, "current": current, "coal": float(r["coal"]), "ore": float(r["ore"]),
                           "copper": float(r["copper"]), "uranium": float(r["uranium"]), "time": r["research_time"], "busy": time_busy})
        else:
            # types.append(row["name"])
            skills.append({"name": name, "current": current, "coal": 0, "ore": 0,
                           "copper": 0, "uranium": 0, "time": 0, "busy": time_busy})            
    return jsonify(skills)


@app.route('/loadplanets', methods=['GET'])
def loadplanets():
    user = request.args.get('user', None)
    fromm = int(request.args.get('from', 0))
    to = int(request.args.get('to', 100))
    sort = request.args.get('sort', "id")
    if to == 0:
        to = 100
        
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    total = table.count()
    i = 1
    stack = []
    if user is None or user == "":
        if sort == "date":
            for row in table.find(_limit=to, order_by="-date_disc"):
                if i > fromm and i <= to:
                    stack.append({"name": row["name"], "username": row["user"], "id": row["id"], "posx": row["cords_hor"], "for_sale": row["for_sale"],
                                  "posy": row["cords_ver"], "starter": row["startplanet"], "bonus": row["bonus"], "planet_type": row["planet_type"], "date": int(row["date_disc"].timestamp())})
                i += 1            
        else:
            for row in table.find(_limit=to):
                if i > fromm and i <= to:
                    stack.append({"name": row["name"], "username": row["user"], "id": row["id"], "posx": row["cords_hor"], "for_sale": row["for_sale"],
                                  "posy": row["cords_ver"], "starter": row["startplanet"], "bonus": row["bonus"], "planet_type": row["planet_type"], "date": int(row["date_disc"].timestamp())})
                i += 1
    else:
        if sort == "date":
            for row in table.find(user=user, _limit=to, order_by="-date_disc"):
                if i > fromm and i <= to:
                    stack.append({"name": row["name"], "username": row["user"], "id": row["id"], "posx": row["cords_hor"], "for_sale": row["for_sale"],
                                  "posy": row["cords_ver"], "starter": row["startplanet"], "bonus": row["bonus"], "planet_type": row["planet_type"], "date": int(row["date_disc"].timestamp())})
                i += 1
        else:
            for row in table.find(user=user, _limit=to):
                if i > fromm and i <= to:
                    stack.append({"name": row["name"], "username": row["user"], "id": row["id"], "posx": row["cords_hor"], "for_sale": row["for_sale"],
                                  "posy": row["cords_ver"], "starter": row["startplanet"], "bonus": row["bonus"], "planet_type": row["planet_type"], "date": int(row["date_disc"].timestamp())})
                i += 1                     

    return jsonify({"planets": stack, "misc": {"total": total}})


@app.route('/loadproduction', methods=['GET'])
def loadproduction():
    planetid = request.args.get('id', None)
    user = request.args.get('user', None)
    if planetid is None:
        return jsonify([])
    if user is None:
        return jsonify([])
        
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    row = table.find_one(id=planetid)
   
    if row is None:
        return jsonify([])

    table = db["users"]
    rowe = table.find_one(username=user)
  
    if rowe is None:
        return jsonify([])

    bunker_level = row['level_bunker']
    coalmine_level = row['level_coal']
    oremine_level = row['level_ore']
    coppermine_level = row['level_copper']
    uraniummine_level = row['level_uranium']
    coaldepot_size = float(row['depot_coal'])
    oredepot_size = float(row['depot_ore'])
    
    copperdepot_size = float(row['depot_copper'])
    uraniumdepot_size = float(row['depot_uranium'])
    planet_name = row['name']
    typeid = row['planet_type']
    bonusid = row['bonus']
    booster = (row['boost_percentage'])
    
    coalbooster_level = rowe['r_coalbooster']
    orebooster_level = rowe['r_orebooster']
    copperbooster_level = rowe['r_copperbooster']
    uraniumbooster_level = rowe['r_uraniumbooster']
    enlargebunker_level = rowe['r_enlargebunker']
    
    if row["shieldprotection_busy"] is not None:
        shieldprotection_busy = int(row["shieldprotection_busy"].timestamp())
    else:
        shieldprotection_busy = 0
    if row["shieldcharge_busy"] is not None:
        shieldcharge_busy = int(row["shieldcharge_busy"].timestamp())
    else:
        shieldcharge_busy = 0
    shieldcharged = row["shieldcharged"]
    
    table = db["planettypes"]
    rowt = table.find_one(type_id=typeid)
    type = rowt['type']
    if type == "earth":
        type = "atmosphere"
    table = db["planetlevels"]
    rowb = table.find_one(rarity=bonusid)
    bonus_rate = (rowb['p_bonus_percentage'])
    bonus_name = rowb['name']
    
    if booster is not None:
        
        table = db["shop"]
        rowbos = table.find_one(boost_percentage=booster)
        if rowbos is not None:
            booster_name = rowbos['name']
        else:
            booster_name = None
    else:
        booster_name = None
    
    table = db["productivity"]
    
    ro = table.find_one(name='coalmine', level=coalmine_level)
    coalproduction = float(ro["coal"])
    
    ro = table.find_one(name='oremine', level=oremine_level)
    oreproduction = float(ro["ore"])
    
    ro = table.find_one(name='coppermine', level=coppermine_level)
    copperproduction = float(ro["copper"])
    
    ro = table.find_one(name='uraniummine', level=uraniummine_level)
    uraniumproduction = float(ro["uranium"])
    
    if enlargebunker_level is None:
        enlargebunker_level = 0
    if bunker_level is None or bunker_level == 0:
        bunker_level = 0

    bunker_protection = (bunker_level * 0.005 + 0.05 + enlargebunker_level * 0.0025)
    if bunker_level == 0:
        bunker_protection = 0
    coalsafe = coaldepot_size * bunker_protection
    oresafe = oredepot_size * bunker_protection
    coppersafe = copperdepot_size * bunker_protection
    uraniumsafe = uraniumdepot_size * bunker_protection
    
    if booster is not None:
        booster *= 2
    
    coal = {"level": coalmine_level, "depot": coaldepot_size, "booster": coalbooster_level, "production": coalproduction, "safe": coalsafe}
    ore = {"level": oremine_level, "depot": oredepot_size, "booster": orebooster_level, "production": oreproduction, "safe": oresafe}
    copper = {"level": coppermine_level, "depot": copperdepot_size, "booster": copperbooster_level, "production": copperproduction, "safe": coppersafe}
    uranium = {"level": uraniummine_level, "depot": uraniumdepot_size, "booster": uraniumbooster_level, "production": uraniumproduction, "safe": uraniumsafe}
    planet = {"type": type, "bonus": bonus_name, "rate": bonus_rate, "rune_name": booster_name, "rune": booster, "planet_name": planet_name,
              "shieldcharge_busy": shieldcharge_busy, "shieldprotection_busy": shieldprotection_busy, "shieldcharged": shieldcharged}
    return jsonify({"coal": coal, "ore": ore, "copper": copper, "uranium": uranium, "misc": planet})

@app.route('/loadcost', methods=['GET'])
def loadcost():
    id = request.args.get('level', 0)
    name = request.args.get('name', None)
    planetID = request.args.get('planetID', None)
    busy = request.args.get('busy', None)
    if planetID is None:
        return jsonify([])
    if busy is None:
        busy = name
    if name is None:
        return jsonify([])
        
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    rows  = table.find_one(id=planetID)
    if rows is None:
        return jsonify([])
    table = db["upgradecosts"]
    row = table.find_one(level=(int(id)+1), name=name)
    if row is None:
        return jsonify([])
    if busy.find("mine") > -1:
        busy = busy.replace("mine", "")
    elif busy.find("center") > -1:
        busy = busy.replace("center", "")
    if busy + "_busy" in rows:
        busyr = rows[busy + "_busy"]
    else:
        busyr = None
    shipyardLevel = rows['level_shipyard']
    if name.find("ship") > -1:
        realTime = ((100-shipyardLevel) / 100) * row["upgrade_time"]
    else:
        realTime = row["upgrade_time"]
    if busyr is None:
        busyr = busy + "_busy"
    return jsonify({"coal": float(row["coal"]), "ore": float(row["ore"]), "copper": float(row["copper"]),
                  "uranium": float(row["uranium"]), "time": realTime, "base": 0,
                  "research": 0, "busy": busyr})

@app.route('/shipyard', methods=['GET'])
def shipyard():
    name = request.args.get('name', None)
    planetid = request.args.get('id', None)
    
    if planetid is None:
        return jsonify([])
    ship_list = []
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    p = table.find_one(id=planetid)
   
    if p is None:
        return jsonify([])
    
    blueprints = []
    if p["blueprints"] is not None:
        blueprints = p["blueprints"].split(",")
    
    table = db["shipstats"]
    shipstats_list = []
    if name is not None:
        row = table.find_one(name=name)
        if row is None:
            return jsonify([])
        shipstats_list.append(row)
    else:
        for row in table.find():
            shipstats_list.append(row)
    for row in shipstats_list:
        name = row["name"]
        blueprint = row["blueprint"]
        ship_class = row["class"]
        table = db["upgradecosts"]
        upgrade_cost_name = row["name"]
        if (upgrade_cost_name[-1] == "1" or upgrade_cost_name[-1] == "2") and row["class"] not in ["Explorer", "Transporter", "Yamato"]:
            upgrade_cost_name = upgrade_cost_name[:-1]        
        ro = table.find_one(name=upgrade_cost_name)
        if ro is None:
            continue
        coal = ro['coal']
        copper = ro['copper']
        ore = ro['ore']
        uranium = ro['uranium']
        if ro['stardust'] is not None:
            stardust = int(ro['stardust'])
        else:
            stardust = 0
        
        cords_hor = p['cords_hor']
        cords_ver = p['cords_ver']
        user = p['user']
        level_shipyard = p['level_shipyard']
        upgrade_time = ro['upgrade_time'] * (1 - 0.01 * level_shipyard)
                
        table = db["users"]
        rd = table.find_one(username=user)
        cur_skill = rd['r_' + ship_class]
        battlespeed_buff = rd["b_battlespeed"]
        level_shipyardskill = rd['r_shipyard']
        
        table = db["ships"]
        ro = table.find_one(type=name, cords_ver=cords_ver, cords_hor= cords_hor, order_by="-busy_until")
        if ro is not None:
            busy_time = int(ro['busy_until'].timestamp())
        else:
            busy_time = None
        if name in blueprints:
            activated = True
        else:
            activated = False
        apply_battlespeed = False
        if battlespeed_buff is not None:
            if battlespeed_buff > datetime.utcnow():
                apply_battlespeed = True 
        base_speed = row["speed"]   
        if apply_battlespeed:
                row["speed"] = row["battlespeed"]

        cost = {"coal": coal, "ore": ore, "copper": copper, "uranium": uranium, "time": upgrade_time, "stardust": stardust}
        ship_list.append({"speed": row["speed"], "consumption": float(row["consumption"]), 
                        "longname": row["longname"], "class": row["class"], "variant": row["variant"],
                        "type": name, "activated": activated,
                        "variant_name": row["variant_name"],
                        "structure": row["structure"], "armor": row["armor"],
                        'shield': row['shield'], 'rocket': row['rocket'], 'bullet': row['bullet'],
                        'laser': row['laser'],
                        'capacity' : row["capacity"], 'busy_until' : busy_time,
                        'skill'  : cur_skill, 'min_level'  : row['shipyard_level'], 'cur_level'  : level_shipyard,
                        'cur_level_skill'  : level_shipyardskill ,'cost' : cost, "blueprint": blueprint, "basespeed": base_speed, "battlespeed": row["battlespeed"], "order": row["order"]})
    if len(ship_list) == 1:
        return jsonify(ship_list[0])
    return jsonify(ship_list)
    
@app.route('/loadgift', methods=['GET'])
def loadgift():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["items"]
    stack = []
    for row in table.find(owner=user, last_owner={'not': None}, activated_trx=None, order_by='item_gifted_at'):
        table = db["shop"]
        ro = table.find_one(itemid=row["itemid"])
        name = ro["name"]
        fromm = row['last_owner']
        time = int(row['item_gifted_at'].timestamp())
        stack.append({"name": name, "from": fromm, "time": time})
    return jsonify(stack)

@app.route('/loadbattle', methods=['GET'])
def loadbattle():
    mission_id = request.args.get('mission_id', None)
    battle_number = request.args.get('battle_number', None)
    limit = request.args.get('limit', 100)

    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["battleresults"]
    stack = []
    missions = []
    if mission_id is not None:
        if battle_number is None:
            
            for row in table.find(mission_id=mission_id):
                missions.append(row)
        else:
            for row in table.find(mission_id=mission_id, battle_number=battle_number):
                missions.append(row)
    else:
        try:
            limit = int(limit)
        except:
            limit = 100
        for row in table.find(order_by="-date", _limit=limit):
            missions.append(row)        
      
    for row in missions:
        row["date"] = int(row['date'].timestamp())
        final_attacker_ships = json.loads(row["final_attacker_ships"])
        final_defender_ships = json.loads(row["final_defender_ships"])
        initial_attacker_ships = json.loads(row["initial_attacker_ships"])
        initial_defender_ships = json.loads(row["initial_defender_ships"])
        ship_list = []
        for pos in initial_attacker_ships:
            ship = initial_attacker_ships[pos]
            ship["pos"] = pos
            ship_list.append(ship)
        row["initial_attacker_ships"] = ship_list
        
        ship_list = []
        for pos in initial_defender_ships:
            ship = initial_defender_ships[pos]
            ship["pos"] = pos
            ship_list.append(ship)
        row["initial_defender_ships"] = ship_list
        
        ship_list = []
        for pos in final_attacker_ships:
            ship = final_attacker_ships[pos]
            ship["pos"] = pos
            ship_list.append(ship)
        row["final_attacker_ships"] = ship_list 
        
        ship_list = []
        for pos in final_defender_ships:
            ship = final_defender_ships[pos]
            ship["pos"] = pos
            ship_list.append(ship)
        row["final_defender_ships"] = ship_list 
        stack.append(row)
    return jsonify(stack)



@app.route('/loadranking', methods=['GET'])
def loadranking():
    sort = request.args.get('sort', 'meta')
    limit = request.args.get('limit', 150)
    page = request.args.get('page', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 150     
    if page is not None:
        try:
            page = int(page)
        except:
            page = None      
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["ranking"]
    stack = []
    if sort == "meta":
        order_by = '-meta_rate'
    elif sort == "meta_rate":
        order_by = '-meta_rate'        
    elif sort == "destroyed":
        order_by = '-destroyed_ships_uranium'
    elif sort == "destroyed_ships_uranium":
        order_by = '-destroyed_ships_uranium'
    elif sort == "explorations":
        order_by = '-explorations'
    elif sort == "planets":
        order_by = '-planets'
    elif sort == "fleet":
        order_by = '-ships'
    elif sort == "meta_skill":
        order_by = '-meta_skill'        
        
    for row in table.find(order_by=order_by, _limit=limit):
        stack.append({"user": row["user"], 'coal' : row['rate_coal'],
                    'ore' : row['rate_ore'],
                    'copper' : row['rate_copper'],
                    'uranium' : row['rate_uranium'],
                    'meta_rate' : row['meta_rate'],
                    'meta_skill' : row['meta_skill'],
                    'explorations' : row['explorations'],
                    'planets' : row['planets'],
                    'ships': row['ships'],
                    'destroyed_ships': row['destroyed_ships'],
                    'destroyed_ships_uranium': float(row['destroyed_ships_uranium'])})
    return jsonify(stack)

@app.route('/loadtranslation', methods=['GET'])
def loadtranslation():
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["translate"]
    stack  = []
    for row in table.find():
        stack.append({'variable' : row["variable"], 'translation' : row["translation"]})
    return jsonify(stack)

@app.route('/loadshop', methods=['GET'])
def loadshop():
    user = request.args.get('user', None)

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["shop"]    
    stack  = []
    for row in table.find(order_by='id'):
        table = db["items"]
        left = table.count(itemid=row["itemid"], date={'>=': (datetime.utcnow() - timedelta(days=1))})
        if row["sales_per_day"] > 0:
            leftt = row["sales_per_day"] - left
        else:
            leftt = None
        if row["max_supply"] is not None:
            
            mleft = table.count(itemid=row["itemid"])
            max_left = row["max_supply"] - mleft
        else:
            max_left = None
        activated_list = []
        if user is not None and row['blueprint'] is not None:
            table = db["planets"]
            for planet in table.find(user=user):
                if planet["blueprints"] is not None:
                    if row['blueprint'] in planet["blueprints"].split(","):
                        activated_list.append(planet["id"])
        elif user is not None and row['boost_percentage'] is not None:
            table = db["planets"]
            for planet in table.find(user=user):
                if planet["boost_percentage"] is not None:
                    if row['boost_percentage'] == planet["boost_percentage"]:
                        activated_list.append(planet["id"])                    
        
        sales_per_day = row["sales_per_day"]
        if sales_per_day < 0:
            sales_per_day = row["max_supply"]
            leftt = max_left
        
        stack.append({'name' : row["name"], 
        'id' : row["itemid"], 
        'imgid' : row["itemid"], 
        'ore' : row["ore"], 
        'coal' : row["coal"], 
        'copper' : row["copper"], 
        'uranium' : row["uranium"],
        'booster' : row["boost_percentage"],
        'total' : sales_per_day,
        'max_supply' : row["max_supply"],
        'blueprint': row['blueprint'],
        'activated_planets': activated_list,
        'max_left' : max_left,
        'left' : leftt,
        "buyable": row["buyable"],
        'cost' : row["price"]})
    return jsonify(stack)

@app.route('/loadfleet', methods=['GET'])
def loadfleet():
    planetid = request.args.get('planetid', None)
    user = request.args.get('user', None)
    
    if user is None:
        return jsonify([])
    if planetid is None:
        return jsonify([])    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    if planetid is not None:
        rows = table.find_one(id=planetid)
        if rows is None:
            return jsonify([])        
        hor = rows["cords_hor"]
        ver = rows["cords_ver"]  
    else:
        hor = None
        ver = None
    
    table = db["missions"]
    active_support_missions = []
    for row in table.find(user=user, cords_hor_dest=hor, cords_ver_dest=ver, mission_type="support", cancel_trx=None):
        active_support_missions.append(row["mission_id"])

    for row in table.find(user=user, cords_hor_dest=hor, cords_ver_dest=ver, mission_type="upgradeyamato", cancel_trx=None):
        if row["busy_until_return"] is not None and row["busy_until_return"] > datetime.utcnow():
            active_support_missions.append(row["mission_id"])

    table = db["shipstats"]
    ship_types = {}
    for ro in table.find():
        ship_types[ro["name"]] = ro

    table = db["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify([])   
    battlespeed_buff = userdata["b_battlespeed"]
    apply_battlespeed = False
    if battlespeed_buff is not None:
        if battlespeed_buff > datetime.utcnow():
            apply_battlespeed = True

    table = db["ships"]
    stack = []
    for row in table.find(user=user, cords_hor=hor, cords_ver=ver, busy_until={'<': datetime.utcnow()}):

        curutc = datetime.utcnow()
        if row["busy_until"] > curutc:
            continue
        if row["mission_busy_until"] is not None and row["mission_busy_until"] > curutc:
            continue
        if hor is not None and hor != row["cords_hor"]:
            continue
        if ver is not None and ver != row["cords_ver"]:
            continue

        ro = ship_types[row["type"]]
        speed = float(ro["speed"])
        if apply_battlespeed:
            speed = float(ro["battlespeed"])
        cons = float(ro["consumption"])
        capacity = float(ro["capacity"])
        longname = ro["longname"]
        order = ro["order"]
        mission_id = row["mission_id"]
        if mission_id is not None:
            if mission_id in active_support_missions:
                continue
          
        stack.append({'id' : row["id"],
        'type' : row["type"],
        'hor' : row["cords_hor"],
        'ver' : row["cords_ver"],
        'busy': int(row["busy_until"].timestamp()),
        'lastupdate': int(row["last_update"].timestamp()),
        'ore' : float(row["qyt_ore"]),
        'uranium' : float(row["qyt_uranium"]),
        'copper' : float(row["qyt_copper"]),
        'coal' : float(row["qyt_coal"]),
        'speed' : speed,
        'cons' : cons,
        'longname': longname,
        'capacity' : capacity,
        'for_sale': row["for_sale"],
        'order': order})
    return jsonify(stack)

@app.route('/planetfleet', methods=['GET'])
def planetfleet():
    planet = request.args.get('planet', None)
    user = request.args.get('user', None)

    if user is None:
        return jsonify([])
    if planet is None:
        return jsonify([])
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})

    table = db["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify([])
    battlespeed_buff = userdata["b_battlespeed"]
    apply_battlespeed = False
    if battlespeed_buff is not None:
        if battlespeed_buff > datetime.utcnow():
            apply_battlespeed = True

    sql=""" SELECT * from shipstats t1
            INNER JOIN (
            SELECT type, COUNT(id) quantity, SUM(for_sale) for_sale
            FROM ships
            WHERE   cords_hor IN (SELECT cords_hor FROM planets WHERE id = '"""+planet+"""')
                AND cords_ver IN (SELECT cords_ver FROM planets WHERE id = '"""+planet+"""')
                AND user = '"""+user+"""'
                AND busy_until < CURRENT_TIMESTAMP
                AND (mission_busy_until is NULL OR mission_busy_until < CURRENT_TIMESTAMP)
                AND (mission_id is NULL OR mission_id NOT IN (  SELECT mission_id
                                                                FROM missions
                                                                WHERE user = '"""+user+"""'
                                                                    AND cords_hor_dest IN (SELECT cords_hor FROM planets WHERE id = '"""+planet+"""')
                                                                    AND cords_ver_dest IN (SELECT cords_ver FROM planets WHERE id = '"""+planet+"""')
                                                                    AND mission_type IN ('support','upgradeyamato')
                                                                    AND cancel_trx is NULL
                                                                    AND mission_busy_until > CURRENT_TIMESTAMP))
                GROUP BY type) t2
            ON t1.name = t2.type
        """
    result = db.query(sql)
    stack = []
    for row in result:
        if apply_battlespeed:
            row["speed"] = row["battlespeed"]
        stack.append({
            "type": row["type"],
            "speed": float(row["speed"]),
            "consumption": float(row["consumption"]),
            "longname": row["longname"],
            "capacity": int(row["capacity"]),
            "for_sale": int(row["for_sale"]),
            "class": row["class"],
            "variant": row["variant_name"],
            "structure": int(row["structure"]),
            "armor": int(row["armor"]),
            "rocket": int(row["rocket"]),
            "bullet": int(row["bullet"]),
            "laser": int(row["laser"]),
            "shipyard_level": int(row["shipyard_level"]),
            "quantity": int(row["quantity"]),
            "order": int(row["order"])
        })

    return jsonify(stack)

@app.route('/planetships', methods=['GET'])
def planetships():
    planet = request.args.get('planet', None)
    user = request.args.get('user', None)
    ship_type = request.args.get('type', None)
    limit = request.args.get('limit', None)

    if user is None:
        return jsonify([])
    if planet is None:
        return jsonify([])
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})

    table = db["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify([])
    battlespeed_buff = userdata["b_battlespeed"]
    apply_battlespeed = False
    if battlespeed_buff is not None:
        if battlespeed_buff > datetime.utcnow():
            apply_battlespeed = True
    type_filter = "1 = 1"
    if ship_type is not None:
        type_filter = "type = '"+ship_type+"'"
    limit_filter = ""
    if limit is not None:
        limit_filter = "LIMIT "+limit

    sql=""" SELECT * from shipstats t1
            INNER JOIN (
            SELECT *
            FROM ships
            WHERE   cords_hor IN (SELECT cords_hor FROM planets WHERE id = '"""+planet+"""')
                AND cords_ver IN (SELECT cords_ver FROM planets WHERE id = '"""+planet+"""')
                AND user = '"""+user+"""'
                AND """+type_filter+"""
                AND busy_until < CURRENT_TIMESTAMP
                AND (mission_busy_until is NULL OR mission_busy_until < CURRENT_TIMESTAMP)
                AND (mission_id is NULL OR mission_id NOT IN (  SELECT mission_id
                                                                FROM missions
                                                                WHERE user = '"""+user+"""'
                                                                    AND cords_hor_dest IN (SELECT cords_hor FROM planets WHERE id = '"""+planet+"""')
                                                                    AND cords_ver_dest IN (SELECT cords_ver FROM planets WHERE id = '"""+planet+"""')
                                                                    AND mission_type IN ('support','upgradeyamato')
                                                                    AND cancel_trx is NULL
                                                                    AND mission_busy_until > CURRENT_TIMESTAMP))
            ) t2
            ON t1.name = t2.type
        """+limit_filter+"""
        """
    result = db.query(sql)
    stack = []
    for row in result:
        if apply_battlespeed:
            row["speed"] = row["battlespeed"]
        stack.append({
            "id": row["id"],
            "type": row["type"],
            "speed": float(row["speed"]),
            "consumption": float(row["consumption"]),
            "longname": row["longname"],
            "capacity": int(row["capacity"]),
            "for_sale": int(row["for_sale"]),
            "class": row["class"],
            "variant": row["variant_name"],
            "structure": int(row["structure"]),
            "armor": int(row["armor"]),
            "rocket": int(row["rocket"]),
            "bullet": int(row["bullet"]),
            "laser": int(row["laser"]),
            "shipyard_level": int(row["shipyard_level"]),
            "order": int(row["order"]),
        })

    return jsonify(stack)


@app.route('/loadcorddata', methods=['GET'])
def loadcorddata():
    x = request.args.get('x', None)
    y = request.args.get('y', None)
    if x is None:
        return jsonify([])
    if y is None:
        return jsonify([])
    type = "nothing"
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    row = table.find_one(cords_hor=x, cords_ver=y)
    if row is None:
        user = None
        name = None
        table = db["space"]
        ro = table.find_one(c_hor=x, c_ver=y)
        if ro is None:
            type = "nothing"
        else:
            type = "explored"        
    else:
        type = "planet"
        user = row['user']
        name = row['name']
        
    return jsonify({"type": type, "user": user, "name": name})

@app.route('/loaditems', methods=['GET'])
def loaditems():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["items"]
    stack = []
    for row in table.find(owner=user, activated_trx=None):
        table = db["shop"]
        ro = table.find_one(itemid=row["itemid"])
        name = ro["name"]
        ore = ro["ore"]
        uranium = ro["uranium"]
        copper = ro["copper"]
        coal = ro["coal"]
        booster = ro["boost_percentage"]
        blueprint = ro["blueprint"]
        table = db["items"]
        total = table.count(owner=user, itemid=row["itemid"], activated_trx=None)
        stack.append({'id' : row["itemid"],
        'imgid' : row["itemid"],
        'uid' : row["uid"],
        'name' : name,
        'total' : total,
        'ore' : ore,
        'uranium' : uranium,
        'copper' : copper,
        'coal' : coal,
        'booster' : booster,
        "blueprint": blueprint,
        "for_sale": row["for_sale"]})
    return jsonify(stack)

@app.route('/loadgalaxy', methods=['GET'])
def loadgalaxy():
    x = request.args.get('x', None)
    y = request.args.get('y', None)
    width = request.args.get('width', 23)
    height = request.args.get('height', 14)
    
    user = request.args.get('user', None)
    if x is None or x == 'null' or x == 'undefined':
        return jsonify([])
    if y is None or y == 'null' or y == 'undefined':
        return jsonify([])
    try:
        width = int(width)
    except:
        width = 23
    try:
        height = int(height)
    except:
        height = 14
    if width > 125:
        width = 125
    if height > 125:
        height = 125
        
    try:
        
        xoffsetleft = int((width ) / 2)
        xoffsetright = (width ) - int((width) / 2)
        yoffsetup = int((height )/ 2)
        yoffsetdown = (height) - int((height) / 2)
        
        xmin = int(float(x)) - xoffsetleft
        xmax = int(float(x)) + xoffsetright
        ymin = int(float(y)) - yoffsetdown
        ymax = int(float(y)) + yoffsetup
    except:
        return jsonify([])
        
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["space"]
    explored = []
    for row in table.find(c_hor={'between': [xmin, xmax]}, c_ver={'between': [ymin, ymax]}):
        explored.append({'x' : row["c_hor"], 'y' : row["c_ver"] , 'type': 'explored',
                         'user': row['user'], 'date': int(row['date'].timestamp())})
    table = db["missions"]
    explore = []
    all_missions = []
    for row in table.find(cords_hor_dest={'between': [xmin, xmax]}, cords_ver_dest={'between': [ymin, ymax]}, busy_until_return={'>': datetime.utcnow()}):
        mission_type = row['mission_type']
        if mission_type == "explorespace":
            mission_type = "explore"
            explore.append({'x' : row["cords_hor_dest"], 'y' : row["cords_ver_dest"], 'start_x' : row["cords_hor"], 'start_y' : row["cords_ver"], 
                            'type': mission_type, 'user' : row['user'], 'ships': row['ships'], 'date': int(row['busy_until'].timestamp()), 'date_return': int(row['busy_until_return'].timestamp())})            
        else:
            explore.append({'x' : row["cords_hor_dest"], 'y' : row["cords_ver_dest"], 'start_x' : row["cords_hor"], 'start_y' : row["cords_ver"], 
                            'type': row['mission_type'], 'user' : row['user'], 'ships': row['ships'], 'date': int(row['busy_until'].timestamp()), 'date_return': int(row['busy_until_return'].timestamp())})

    for row in table.find(cords_hor_dest={'between': [xmin, xmax]}, cords_ver_dest={'between': [ymin, ymax]}, busy_until_return=None, busy_until={'>': datetime.utcnow()}):
        mission_type = row['mission_type']
        explore.append({'x' : row["cords_hor_dest"], 'y' : row["cords_ver_dest"], 'start_x' : row["cords_hor"], 'start_y' : row["cords_ver"], 
                        'type': row['mission_type'], 'user' : row['user'], 'ships': row['ships'], 'date': int(row['busy_until'].timestamp()), 'date_return': None})

    for row in table.find(cords_hor_dest={'between': [xmin, xmax]}, cords_ver_dest={'between': [ymin, ymax]}, busy_until_return=None, cancel_trx=None, mission_type="support"):
        mission_type = row['mission_type']
        explore.append({'x' : row["cords_hor_dest"], 'y' : row["cords_ver_dest"], 'start_x' : row["cords_hor"], 'start_y' : row["cords_ver"], 
                        'type': row['mission_type'], 'user' : row['user'], 'ships': row['ships'], 'date': int(row['busy_until'].timestamp()), 'date_return': None})

    table = db["planets"]
    planets = []
    for row in table.find(cords_hor={'between': [xmin, xmax]}, cords_ver={'between': [ymin, ymax]}):
        tx = row["cords_hor"]
        ty = row["cords_ver"]
        table = db["planetlevels"]
        rows = table.find_one(rarity=row["bonus"])
        rarity = rows["name"]
        
        table = db["planettypes"]
        rows = table.find_one(type_id=row["planet_type"])
        type = rows["type"]
        img = ""
        img = GetPlanetImg(rarity, type, row['img_id'])
        planets.append({'x': tx, 'y': ty, 'type': 'planet', 'id': row['id'], 'img': img, 'abandoned': row["abandoned"], 'user': row["user"]})
    area = {'xmin' : xmin, 'xmax' : xmax, 'ymin' : ymin, 'ymax' : ymax}
    return jsonify({'explored' : explored, 'explore' : explore, 'planets' : planets, 'area' : area})
        
@app.route('/loadfleetmission', methods=['GET'])
def loadfleetmission():

    planetid = request.args.get('planetid', None)
    user = request.args.get('user', None)
    active = request.args.get('active', None)
    outgoing = request.args.get('outgoing', None)
    onlyuser = request.args.get('onlyuser', None)
    hold = request.args.get('hold', None)
    limit = request.args.get('limit', None)
    page = request.args.get('page', None)
    if user is None:
        return jsonify([])
    if active is not None:
        try:
            active = int(active)
        except:
            return jsonify([])
    if hold is not None:
        
        try:
            hold = int(hold)
        except:
            return jsonify([])      
        
    if onlyuser is not None:
        
        try:
            onlyuser = int(onlyuser)
        except:
            return jsonify([])         
    if outgoing is not None:
        
        try:
            outgoing = int(outgoing)
        except:
            return jsonify([])
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = None     
    if page is not None:
        try:
            page = int(page)
        except:
            page = 0
    else:
        page = 0
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    planet_list = []
    if planetid is None and user is not None:
        for planet in table.find(user=user):
            planet_list.append(planet)
    elif planetid is not None:
        idrow = table.find_one(id=planetid)
        if idrow is None:
            return jsonify([])
        planet_list.append(idrow)
            

    stackold = []
    stack = []
    stackuser = []
    
    missions_list = []
    missions_list_user = []
    mission_id_list = []
    
    for idrow in planet_list:

        posx = idrow["cords_hor"]
        posy = idrow["cords_ver"]    
        table = db["missions"]
        if onlyuser == 1 and user is not None:
            if active == 1:
                
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return={'>': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'>': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)                    
            elif active == 0 and limit is None and False:
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy,  busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)
            elif active == 0 and limit is not None and False:
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return=None, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return=None, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)                    
            elif limit is not None:
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, order_by='-busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, order_by='-busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)                   
            else:
                
                for row in table.find(user=user, cords_hor=posx, cords_ver=posy, order_by='-busy_until'):
                    missions_list.append(row)
                for row in table.find(user=user, cords_hor_dest=posx, cords_ver_dest=posy, order_by='-busy_until'):
                    missions_list.append(row)            
        else:
            if active == 1:
                
                for row in table.find(cords_hor=posx, cords_ver=posy, busy_until_return=None, order_by='-busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return=None, order_by='-busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor=posx, cords_ver=posy, busy_until_return={'>': datetime.utcnow()}, order_by='-busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'>': datetime.utcnow()}, order_by='-busy_until'):
                    missions_list.append(row)                    
            elif active == 0 and limit is None and False:
                for row in table.find(cords_hor=posx, cords_ver=posy, mission_type="explorespace", busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, mission_type="explorespace", busy_until_return=None, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor=posx, cords_ver=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until'):
                    missions_list.append(row)
            elif active == 0 and limit is not None and False:
                for row in table.find(cords_hor=posx, cords_ver=posy, mission_type="explorespace", busy_until_return=None, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, mission_type="explorespace", busy_until_return=None, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(cords_hor=posx, cords_ver=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, busy_until_return={'<': datetime.utcnow()}, order_by='busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)                    
            elif limit is not None:
                for row in table.find(cords_hor=posx, cords_ver=posy, order_by='-busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, order_by='-busy_until', _limit=limit*(page+1)):
                    missions_list.append(row)                
            else:
                for row in table.find(cords_hor=posx, cords_ver=posy, order_by='-busy_until'):
                    missions_list.append(row)
                for row in table.find(cords_hor_dest=posx, cords_ver_dest=posy, order_by='-busy_until'):
                    missions_list.append(row)
                
    if active == 0:
        missions_list = sorted(missions_list, key=lambda m: m["busy_until"], reverse=True)
    else:
        missions_list = sorted(missions_list, key=lambda m: m["busy_until"], reverse=True)

    if page is None and limit is not None:
        missions_list = missions_list[:limit]
    elif page is not None and limit is not None:
        if len(missions_list) < limit * page:
            return jsonify([])
        if len(missions_list) < limit * (page + 1):
            missions_list = missions_list[limit * page:]
        else:
            missions_list = missions_list[limit * page:limit * (page + 1)]          
    i = 0
    for row in missions_list:
        i += 1
        id  = row['mission_id']
        mission_user = row['user']
        if id in mission_id_list:
            continue
        type = row['mission_type']
        if row['busy_until'] is not None:
            arrival = int(row['busy_until'].timestamp())
        else:
            arrival = None
        if row['date'] is not None:
            start_date = int(row['date'].timestamp())
        else:
            start_date = None        
        if row['busy_until_return'] is not None:
            busy_return = int(row['busy_until_return'].timestamp())
        else:
            busy_return = None
        if datetime.utcnow() > row['busy_until'] and busy_return is not None:
            arrival = busy_return
        start_x = row['cords_hor']
        start_y = row['cords_ver']
        end_x = row['cords_hor_dest']
        end_y = row['cords_ver_dest']

        if row["cancel_trx"] is None:
            
            if row['busy_until'] > datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 1:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 0:
                    continue
                elif hold == 1:
                    continue
                elif active == 0:
                    continue
            elif row['busy_until_return'] is not None and row['busy_until_return'] > datetime.utcnow() and row['busy_until'] < datetime.utcnow() and (row["mission_type"] == "siege" or row["mission_type"] == "upgradeyamato"):
                if outgoing == 1:
                    continue
                elif outgoing == 0:
                    continue
                elif hold == 0:
                    continue
                elif active == 0:
                    continue                 
            elif row['busy_until_return'] is not None and row['busy_until'] < datetime.utcnow() and row['busy_until_return'] > datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 0:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 1:
                    continue
                elif hold == 1:
                    continue
                elif active == 0:
                    continue
            elif row['busy_until_return'] is not None and row['busy_until_return'] < datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 0:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 1:
                    continue
                elif hold == 1:
                    continue
                elif active == 1:
                    continue             
                
            elif row['busy_until_return'] is None and row['busy_until'] < datetime.utcnow() and (row["mission_type"] == "support" or row["mission_type"] == "siege" or row["mission_type"] == "upgradeyamato"):
                if outgoing == 1:
                    continue
                elif outgoing == 0:
                    continue
                elif hold == 0:
                    continue
                elif active == 0:
                    continue                    
            elif row['busy_until_return'] is None and row['busy_until'] < datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 1:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 0:
                    continue                    
                elif hold == 0:
                    continue
                elif active == 1:
                    continue                      
        else:
            if row['busy_until'] > datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 0:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 1:
                    continue
                elif hold == 1:
                    continue
                elif active == 0:
                    continue
            elif row['busy_until_return'] is not None and row['busy_until'] < datetime.utcnow() and row['busy_until_return'] > datetime.utcnow():
                if end_x == posx and end_y == posy and outgoing == 0:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 1:
                    continue
                elif hold == 1:
                    continue
                elif active == 0:
                    continue                    
            else:
                if end_x == posx and end_y == posy and outgoing == 0:
                    continue
                elif start_x == posx and start_y == posy and outgoing == 1:
                    continue
                elif hold == 1:
                    continue
                elif active == 1:
                    continue                    
        table = db["planets"]
        from_planet_data = table.find_one(cords_hor=start_x, cords_ver=start_y)
        to_planet_data = table.find_one(cords_hor=end_x, cords_ver=end_y)
        table = db["battleresults"]
        battle_number = table.count(mission_id=id)
        table = db["activity"]
        rows = table.find_one(mission_id=id)
        if rows is not None:
            resulte = rows["result"]
            if resulte == "1" and rows["user"] != mission_user:
                resulte = "2"
            elif resulte == "2" and rows["user"] != mission_user:
                resulte = "1"
            new_planet_id = rows["new_planet_id"]
            new_item_id = rows["new_item_id"]
            new_stardust = rows["new_stardust"]
            if new_stardust is not None:
                new_stardust = int(new_stardust)            
        else:
            resulte = None
            new_planet_id = None
            new_item_id = None
            new_stardust = None  
        try:
            ships_dict = json.loads(row['ships'])
            ships = {}
            shipTotal = 0
            pos = 1
            for ship in ships_dict:
                ships[ship] = {"n": int(ships_dict[ship]), "pos": pos}
                pos += 1
                shipTotal += int(ships_dict[ship])
                

            ships['total'] = shipTotal             
        except:
            ships = {}
            shipTotal = 0
        if shipTotal == 0:
            
            shipTotal = row['n_explorership'] + row['n_transportship'] + row['n_corvette'] + row['n_frigate']
            shipTotal = shipTotal + row['n_destroyer'] + row['n_cruiser'] + row['n_battlecruiser']
            shipTotal = shipTotal + row['n_carrier']  + row['n_dreadnought']
            ships_dict = {'explorership' : row['n_explorership'],
                'transportship' : row['n_transportship'],
                'corvette' : row['n_corvette'],
                'frigate' : row['n_frigate'],
                'destroyer' : row['n_destroyer'],
                'cruiser' : row['n_cruiser'],
                'battlecruiser' : row['n_battlecruiser'],
                'carrier' : row['n_carrier'],
                'dreadnought' : row['n_dreadnought']}
            shipTotal = 0
            pos = 1
            ships = {}
            for ship in ships_dict:
                ships[ship] = {"n": int(ships_dict[ship]), "pos": pos}
                pos += 1
                shipTotal += int(ships_dict[ship])
                

            ships['total'] = shipTotal                 
        if from_planet_data is not None:
            table = db["planetlevels"]
            rows = table.find_one(rarity=from_planet_data['bonus'])
            bonus = rows["p_bonus_percentage"]
            rarity = rows["name"]
            typenumber = 0
            if from_planet_data['planet_type'] == 0:
                typenumber = 1
            else:
                typenumber = from_planet_data['planet_type']
            
            table = db["planettypes"]
            rows = table.find_one(type_id=typenumber)
            planet_type = rows["type"]                   
            from_planet = { "name": from_planet_data["name"], 
                            "user": from_planet_data["user"], 
                            'bonus': rarity,
                            # 'rarity': rarity,
                            "planet_type": planet_type, 
                            "id": from_planet_data["id"],
            }
        else:
            from_planet = None
        if to_planet_data is not None:
            
            table = db["planetlevels"]
            rows = table.find_one(rarity=to_planet_data['bonus'])
            bonus = rows["p_bonus_percentage"]
            rarity = rows["name"]
            typenumber = 0
            if to_planet_data['planet_type'] == 0:
                typenumber = 1
            else:
                typenumber = to_planet_data['planet_type']
            
            table = db["planettypes"]
            rows = table.find_one(type_id=typenumber)
            planet_type = rows["type"]                
            
            to_planet = { "name": to_planet_data["name"], 
                            "user": to_planet_data["user"], 
                            'bonus': rarity,
                            #'rarity': rarity,
                            "planet_type": planet_type, 
                            "id": to_planet_data["id"],
            }   
        else:
            to_planet = None
        resources = {        'coal' : float(row['qyt_coal']),
        'ore' : float(row['qyt_ore']),
        'copper' : float(row['qyt_copper']),
        'uranium' : float(row['qyt_uranium'])}
        arr = {    'id' : id,
        'type' : type,
        'user': mission_user,
        'start_date': start_date,
        'arrival' : arrival,
        'return' : busy_return,
        'start_x' : start_x,
        'start_y' : start_y,
        'end_x' : end_x,
        'end_y' : end_y,
        'ships' : ships,
        'cancel_trx': row['cancel_trx'],
        'resources' : resources,
        "from_planet": from_planet,
        "to_planet": to_planet,
        'result':  resulte,
        "new_planet_id": new_planet_id,
        "new_item_id": new_item_id,
        "new_stardust": new_stardust,
        "battles": battle_number}
        stack.append(arr)
        mission_id_list.append(id)            
        
    return jsonify(stack)

@app.route('/loadplanet', methods=['GET'])
def loadplanet():
    id = request.args.get('id', None)
    x = request.args.get('x', None)
    y = request.args.get('y', None)    
    if id is None and (x is None or y is None):
        return jsonify([])
        
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    if id is not None:
        row = table.find_one(id=id)
    else:
        row = table.find_one(cords_hor=x, cords_ver=y)
        
    if row is None:
        return jsonify([])
    if id is None:
        id = row["id"]
    table = db["planetlevels"]
    rows = table.find_one(rarity=row['bonus'])
    bonus = rows["p_bonus_percentage"]
    rarity = rows["name"]
    typenumber = 0
    if row['planet_type'] == 0:
        typenumber = 1
    else:
        typenumber = row['planet_type']
    
    table = db["planettypes"]
    rows = table.find_one(type_id=typenumber)
    type = rows["type"]
    table = db["planets"]
    total_type = table.count(planet_type=typenumber, bonus=row['bonus'])
    
    img = GetPlanetImg(rarity,type, row['img_id'])
    cr_date_ts = int(row["date_disc"].timestamp())
    if row["shieldprotection_busy"] is not None:
        shieldprotection_busy = int(row["shieldprotection_busy"].timestamp())
    else:
        shieldprotection_busy = 0
    if row["shieldcharge_busy"] is not None:
        shieldcharge_busy = int(row["shieldcharge_busy"].timestamp())
    else:
        shieldcharge_busy = 0
    shieldcharged = row["shieldcharged"]  
        
    
    return jsonify({'planet_name' : row['name'],
         'planet_id' : id,
         'total_type' : total_type,
         'user' : row["user"],
         'planet_type' : type,
         'planet_bonus' : bonus,
         'planet_rarity' : rarity,
         'planet_corx' : row["cords_hor"],
         'planet_cory' : row["cords_ver"],
         'planet_crts' : cr_date_ts,
         'img' : img,
         'level_base' : row["level_base"],
         'level_coal' : row["level_coal"],
         'level_ore' : row['level_ore'],
         'level_copper' : row['level_copper'],
         'level_uranium' : row['level_uranium'],
         'level_ship' : row['level_shipyard'],
         'level_research' : row['level_research'],
         'level_coaldepot' : row['level_coaldepot'],
         'level_oredepot' : row['level_oredepot'],
         'level_copperdepot' : row['level_copperdepot'],
         'level_uraniumdepot' : row['level_uraniumdepot'],
         'shieldcharge_busy': shieldcharge_busy,
         'shieldprotection_busy': shieldprotection_busy,
         'shieldcharged': shieldcharged,
         'startplanet': row['startplanet'],
         'abandoned': row['abandoned'],
         'for_sale': row['for_sale']
         })
    
@app.route('/transactions', methods=['GET'])
def transactions():
    limit = request.args.get('limit', 150)
    tr_type = request.args.get('type', None)
    user = request.args.get('user', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 150       

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["transactions"]
    trx_list = []
    if tr_type is None and user is None:
        for trx in table.find(order_by='-date', error=None, virtualop=0, _limit=limit):
            trx["date"] = int(trx["date"].timestamp())
            trx_list.append(trx)

    if tr_type is not None and user is None:
        for trx in table.find(order_by='-date', error=None, virtualop=0, tr_type=tr_type, _limit=limit):
            trx["date"] = int(trx["date"].timestamp())
            trx_list.append(trx)        

    if tr_type is None and user is not None:
        for trx in table.find(order_by='-date', error=None, virtualop=0, user=user, _limit=limit):
            trx["date"] = int(trx["date"].timestamp())
            trx_list.append(trx)     

    if tr_type is not None and user is not None:
        for trx in table.find(order_by='-date', error=None, virtualop=0, tr_type=tr_type, user=user, _limit=limit):
            trx["date"] = int(trx["date"].timestamp())
            trx_list.append(trx)             

    if len(trx_list) == 0:
        return jsonify([])

    return jsonify(trx_list)

@app.route('/state', methods=['GET'])
def state():

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["status"]
    status = table.find_one(id=1)
    last_steem_block_num = status["last_steem_block_num"]
    if status["tracker_stop_block_num"] > status["last_steem_block_num"]:
        last_steem_block_num = status["tracker_stop_block_num"]
        
    processing_delay_seconds = (last_steem_block_num - status["first_unprocessed_block_num"]) * 3
    tracker_delay_seconds = (last_steem_block_num - status["latest_block_num"]) * 3
    return jsonify({"latest_block_num": last_steem_block_num, "first_unprocessed_block_num": status["first_unprocessed_block_num"],
                    "tracker_block_num": status["latest_block_num"], "processing_delay_seconds": processing_delay_seconds,
                    "tracker_delay_seconds": tracker_delay_seconds})

@app.route('/season', methods=['GET'])
def season():
    timestamp = request.args.get('timestamp', None)

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["season"]
    if timestamp is None:
        season = table.find_one(order_by="-end_date")
    else:
        queryDate = datetime.fromtimestamp(int(timestamp))
        season = table.find_one(end_date={'>': queryDate}, start_date={'<': queryDate})
    
    if season is None:
        return jsonify({}) 

    if season["leach_rate"] is not None:
        season["leach_rate"] = float(season["leach_rate"])
    else:
        season["leach_rate"] = 0      

    if season["deploy_rate"] is not None:
        season["deploy_rate"] = float(season["deploy_rate"])
    else:
        season["deploy_rate"] = 0    

    return jsonify({"id": season["id"], "start_date": int(season["start_date"].timestamp()), "end_date": int(season["end_date"].timestamp()),
                   "steem_rewards": float(season["steem_rewards"]), "name": season["name"], "leach_rate": season["leach_rate"], "deploy_rate": float(season["deploy_rate"])})

@app.route('/seasonranking', methods=['GET'])
def seasonranking():
    sort = request.args.get('sort', 'total_reward')
    limit = request.args.get('limit', 150)
    timestamp = request.args.get('timestamp', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 150     
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["season"]
    
    if timestamp is None:
        season = table.find_one(order_by="-end_date")
    else:
        queryDate = datetime.fromtimestamp(int(timestamp))
        season = table.find_one(end_date={'>': queryDate}, start_date={'<': queryDate})
    if season is None:
        return jsonify({})   
    else:
        season_id = int(season['id'])

    table = db["seasonranking"]
    stack = []
    if sort == "total_reward":
        order_by = '-total_reward'
    elif sort == "build_reward":
        order_by = '-build_reward'        
    elif sort == "destroy_reward":
        order_by = '-destroy_reward'   
        
    for row in table.find(order_by=order_by, season_id=season_id, _limit=limit):
        stack.append({"user": row["user"], 'build_reward' : row['build_reward'],
                    'destroy_reward' : row['destroy_reward'],
                    'total_reward' : row['total_reward'],
                    'season_id' : row['season_id']})
    
    if season["leach_rate"] is not None:
        season["leach_rate"] = float(season["leach_rate"])
    else:
        season["leach_rate"] = 0           
    
    if season["deploy_rate"] is not None:
        season["deploy_rate"] = float(season["deploy_rate"])
    else:
        season["deploy_rate"] = 0         

    return jsonify({"id": season["id"], "start_date": int(season["start_date"].timestamp()), "end_date": int(season["end_date"].timestamp()),
                   "steem_rewards": float(season["steem_rewards"]), "name": season["name"], "leach_rate": float(season["leach_rate"]), "deploy_rate": float(season["deploy_rate"]), "ranking": stack})

@app.route('/activateditems', methods=['GET'])
def activateditems():
    user = request.args.get('user', None)
    planetid = request.args.get('planetid', None)
    if user is None:
        return jsonify([]) 
    if planetid is None:
        return jsonify([]) 

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table_items = db["items"]
    stack = []
    for row in table_items.find(owner=user, activated_to=planetid):
        table = db["shop"]
        ro = table.find_one(itemid=row["itemid"])
        name = ro["name"]
        ore = ro["ore"]
        uranium = ro["uranium"]
        copper = ro["copper"]
        coal = ro["coal"]
        booster = ro["boost_percentage"]
        blueprint = ro["blueprint"]
        stack.append({'id' : row["itemid"],
        'imgid' : row["itemid"],
        'uid' : row["uid"],
        'name' : name,
        'ore' : ore,
        'uranium' : uranium,
        'copper' : copper,
        'coal' : coal,
        'booster' : booster,
        "blueprint": blueprint,
        "activated_date": int(row["activated_date"].timestamp())})
    return jsonify(stack)

@app.route('/missions', methods=['GET'])
def missions():
    limit = request.args.get('limit', 100)
    user = request.args.get('user', None)
    mission_type = request.args.get('mission_type', None)
    cords_hor = request.args.get('cords_hor', None)
    cords_ver = request.args.get('cords_ver', None)
    cords_hor_dest = request.args.get('cords_hor_dest', None)
    cords_ver_dest = request.args.get('cords_ver_dest', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 100      

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["missions"]
    mission_list = []  
    
    filter = {"order_by": '-busy_until', "_limit": limit}
    if user is not None:
        filter.update({"user": user})
    if mission_type is not None:
        filter.update({"mission_type": mission_type})
    if cords_hor is not None:
        filter.update({"cords_hor": cords_hor})
    if cords_ver is not None:
        filter.update({"cords_ver": cords_ver})
    if cords_hor_dest is not None:
        filter.update({"cords_hor_dest": cords_hor_dest})
    if cords_ver_dest is not None:
        filter.update({"cords_ver_dest": cords_ver_dest}) 

    for mission in table.find(**filter):
        mission["busy_until"] = int(mission["busy_until"].timestamp())
        mission["date"] = int(mission["date"].timestamp())
        if mission["busy_until_return"] is not None:
            mission["busy_until_return"] = int(mission["busy_until_return"].timestamp())
        if mission["ships"] is not None:
            mission["ships"] = json.loads(mission["ships"])
        if mission["ships"] is None:
            mission["ships"] = {'explorership' : mission['n_explorership'],
                'transportship' : mission['n_transportship'],
                'corvette' : mission['n_corvette'],
                'frigate' : mission['n_frigate'],
                'destroyer' : mission['n_destroyer'],
                'cruiser' : mission['n_cruiser'],
                'battlecruiser' : mission['n_battlecruiser'],
                'carrier' : mission['n_carrier'],
                'dreadnought' : mission['n_dreadnought']}

        table = db["battleresults"]
        battle_number = table.count(mission_id=mission["mission_id"])
        table = db["activity"]
        rows = table.find_one(mission_id=mission["mission_id"])
        if rows is not None:
            result = rows["result"]
            new_planet_id = rows["new_planet_id"]
            new_item_id = rows["new_item_id"]
            new_stardust = rows["new_stardust"]
            if new_stardust is not None:
                new_stardust = int(new_stardust)            
        else:
            result = None  
            new_planet_id = None
            new_item_id = None
            new_stardust = None  

        mission_clean = {"busy_until": mission["busy_until"], "busy_until_return": mission["busy_until_return"],
        "cords_hor": mission["cords_hor"],"cords_ver": mission["cords_ver"],
        "cords_hor_dest": mission["cords_hor_dest"],"cords_ver_dest": mission["cords_ver_dest"],
        "date": mission["date"], "mission_id": mission["mission_id"], "mission_type": mission["mission_type"],
        "qyt_coal": mission["qyt_coal"], "qyt_ore": mission["qyt_ore"], "qyt_copper": mission["qyt_copper"],
        "ships": mission["ships"], "user": mission["user"], "result": result, "new_planet_id": new_planet_id,
        "new_item_id": new_item_id, "new_stardust": new_stardust, "battles": battle_number }
        
        mission_list.append(mission_clean)           

    if len(mission_list) == 0:
        return jsonify([])

    return jsonify(mission_list)

@app.route('/burnrates', methods=['GET'])
def burnrates():
   return jsonify([{"bonus": "4", "planet_type": "5", "burnrate": 9000000 * 1e8},
                   {"bonus": "4", "planet_type": "4", "burnrate": 7000000 * 1e8},
                   {"bonus": "4", "planet_type": "3", "burnrate": 6000000 * 1e8},
                   {"bonus": "4", "planet_type": "2", "burnrate": 5000000 * 1e8},
                   {"bonus": "4", "planet_type": "1", "burnrate": 3000000 * 1e8},
                   {"bonus": "3", "planet_type": "5", "burnrate": 90000 * 1e8},
                   {"bonus": "3", "planet_type": "4", "burnrate": 70000 * 1e8},
                   {"bonus": "3", "planet_type": "3", "burnrate": 60000 * 1e8},
                   {"bonus": "3", "planet_type": "2", "burnrate": 50000 * 1e8},
                   {"bonus": "3", "planet_type": "1", "burnrate": 30000 * 1e8},
                   {"bonus": "2", "planet_type": "5", "burnrate": 30000 * 1e8},
                   {"bonus": "2", "planet_type": "4", "burnrate": 25000 * 1e8},
                   {"bonus": "2", "planet_type": "3", "burnrate": 20000 * 1e8},
                   {"bonus": "2", "planet_type": "2", "burnrate": 18000 * 1e8},
                   {"bonus": "2", "planet_type": "1", "burnrate": 10000 * 1e8},
                   {"bonus": "1", "planet_type": "5", "burnrate": 15000 * 1e8},
                   {"bonus": "1", "planet_type": "4", "burnrate": 12000 * 1e8},
                   {"bonus": "1", "planet_type": "3", "burnrate": 10000 * 1e8},
                   {"bonus": "1", "planet_type": "2", "burnrate": 9000 * 1e8},
                   {"bonus": "1", "planet_type": "1", "burnrate": 5000 * 1e8},
                   ])


@app.route('/galaxyplanets', methods=['GET'])
def galaxplanets():
    limit = request.args.get('limit', 100000)
    after = request.args.get('after', None)
    
    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 100000       
    if after is not None:
        try:
            queryDate = datetime.fromtimestamp(int(after))
        except:
            queryDate = datetime.utcnow()

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["planets"]
    planet_list = []  
    
    filter = {"order_by": "-last_update", "_limit": limit}
    if after is not None:      
        filter.update({"last_update": {'>': queryDate}})

    for planet in table.find(**filter):
        planet_small = {"x":planet["cords_hor"], "y":planet["cords_ver"], "id": planet["id"],  "update": int(planet["last_update"].timestamp()),
                        "user": planet["user"], "bonus": planet["bonus"], "type": planet["planet_type"],
                        "name": planet["name"], "starter": planet["startplanet"], "abandoned": planet["abandoned"], "for_sale": planet["for_sale"], "img_id": planet["img_id"]}
        planet_list.append(planet_small)           

    if len(planet_list) == 0:
        return jsonify([])

    return jsonify(planet_list)

@app.route('/asks', methods=['GET'])
def asks():
    limit = request.args.get('limit', 100)
    user = request.args.get('user', None)
    category = request.args.get('category', None)
    subcategory = request.args.get('subcategory', None)
    itype = request.args.get('type', None)
    active = request.args.get('active', None)
    sold = request.args.get('sold', None)
    id = request.args.get('id', None)
    uid = request.args.get('uid', None)
    market = request.args.get('market', None)
    orderby = request.args.get('orderby', 'price')
    order = request.args.get("order", "asc")

    if limit is not None:
        try:
            limit = int(limit)
        except:
            limit = 100  
    if order == "asc":
        orderkey = ""
    if order == "desc":
        orderkey = "-"  

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["asks"]
    ask_list = []  
    
    filter = {"order_by": orderkey+orderby, "_limit": limit}
    if user is not None:
        filter.update({"user": user})
    if category is not None:
        filter.update({"category": category})
    if subcategory is not None:
        filter.update({"subcategory": subcategory})
    if itype is not None:
        filter.update({"type": itype})                
    if active == "1":
        filter.update({"failed": None, "sold": None, "cancel_trx": None, "buy_trx": None})
    if sold == "1":
        filter.update({"sold": {'not': None}})
    if uid is not None:
        filter.update({"uid": uid})
    if id is not None:
        filter.update({"id": id})
    if market is not None:
        filter.update({"market": market})

    for ask in table.find(**filter):
        ask["date"] = int(ask["date"].timestamp())
        if ask["sold"] is not None:
            ask["sold"] = int(ask["sold"].timestamp())
        if ask["failed"] is not None:
            ask["failed"] = int(ask["failed"].timestamp())

        ask_clean = {"id": ask["id"], "uid": ask["uid"], "category": ask["category"], "subcategory": ask["subcategory"],  "type": ask["type"], "price": ask["price"], "fee_market": ask["fee_market"],
                     "market": ask["market"], "date": ask["date"], "user": ask["user"],"cancel_trx": ask["cancel_trx"], "buy_trx": ask["buy_trx"], "sold": ask["sold"],
                     "failed": ask["failed"], "cords_hor": ask["cords_hor"], "cords_ver": ask["cords_ver"], "fee_burn": ask["fee_burn"], "img_id": ask["img_id"]}
        
        ask_list.append(ask_clean)           

    if len(ask_list) == 0:
        return jsonify([])

    return jsonify(ask_list)

@app.route('/lowestasks', methods=['GET'])
def lowestasks():
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})

    sql =    """SELECT * FROM (SELECT * FROM `asks` WHERE cancel_trx is null AND buy_trx is null and sold is null and failed is null) t5
                INNER JOIN
                    (SELECT utype utype3, min(price) price3, MIN(date) date3
                    FROM
                        (SELECT *
                        FROM (SELECT * FROM `asks` WHERE cancel_trx is null AND buy_trx is null and sold is null and failed is null) t3
                        INNER JOIN (SELECT utype utype2, MIN(price) price2
                                    FROM asks
                                    WHERE cancel_trx is null AND buy_trx is null and sold is null and failed is null GROUP BY utype) t1 
                    ON t3.utype = t1.utype2 AND t3.price = t1.price2) t4
                    group by utype) t6
                ON t5.utype = t6.utype3 AND t5.price = t6.price3 AND t5.date = t6.date3
                ORDER by PRICE ASC"""
    result = db.query(sql)
    ask_list = []  
    for ask in result:
        ask["date"] = int(ask["date"].timestamp())
        if ask["sold"] is not None:
            ask["sold"] = int(ask["sold"].timestamp())
        if ask["failed"] is not None:
            ask["failed"] = int(ask["failed"].timestamp())
        ask_clean = {"id": ask["id"], "uid": ask["uid"], "category": ask["category"], "subcategory": ask["subcategory"],  "type": ask["type"], "price": ask["price"], "fee_market": ask["fee_market"],
                     "market": ask["market"], "date": ask["date"], "user": ask["user"],"cancel_trx": ask["cancel_trx"], "buy_trx": ask["buy_trx"], "sold": ask["sold"],
                     "failed": ask["failed"], "cords_hor": ask["cords_hor"], "cords_ver": ask["cords_ver"], "fee_burn": ask["fee_burn"] }
        
        ask_list.append(ask_clean)           

    if len(ask_list) == 0:
        return jsonify([])

    return jsonify(ask_list)


@app.route('/missionoverview', methods=['GET'])
def missionoverview():
    user = request.args.get('user',None)

    if user is None:
        return jsonify([])

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify([])
    missioncontrol = userdata["r_missioncontrol"]
    missioncontrol_buff = userdata["b_missioncontrol"]
    if missioncontrol is not None:
        max_missions = int(missioncontrol) * 2
    else:
        max_missions = 0
    if missioncontrol_buff is not None and missioncontrol_buff > datetime.utcnow():
        max_missions = 400

    sql = """SELECT COUNT(*) active_missions
             FROM missions
             WHERE user = '"""+user+"""'
               AND (                  
                    (busy_until > CURRENT_TIMESTAMP AND busy_until_return is NULL AND cancel_trx is NULL)
                    OR (busy_until_return > CURRENT_TIMESTAMP AND cancel_trx is NULL)
                    OR (mission_type = "support" AND cancel_trx is NULL)
            )"""
    result = db.query(sql)
    active_missions = 0
    for row in result:
        active_missions = int(row['active_missions']) 
    free_missions = max_missions - active_missions

    sql = """SELECT mission_type
             FROM missions
             WHERE CONCAT(cords_hor_dest,'/',cords_ver_dest) IN (SELECT CONCAT(cords_hor,'/',cords_ver)
                                                                   FROM planets
                                                                  WHERE user = '"""+user+"""')
                                                                    AND user !='"""+user+"""'
                                                                    AND (                  
                                                                         (busy_until > CURRENT_TIMESTAMP AND busy_until_return is NULL)
                                                                         OR (busy_until_return > CURRENT_TIMESTAMP)
                                                                         OR (mission_type = "support" AND cancel_trx is NULL)
          )"""
    result = db.query(sql)
    friendly_count = 0
    hostile_count = 0
    for row in result:
        if row["mission_type"] == "siege" or row["mission_type"] == "attack":
            hostile_count += 1
        if row["mission_type"] == "support" or row["mission_type"] == "breaksiege" or row["mission_type"] == "deploy" or row["mission_type"] == "transport":
            friendly_count +=1


    response = {"free_missions": free_missions ,"max_missions": max_missions, "own_missions": active_missions, "hostile_missions": hostile_count, "friendly_missions": friendly_count}

    return jsonify(response)

@app.route("/dailybattles", methods=['GET'])
def dailybattles():
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    sql = """SELECT mission_id, date, attacker, defender, (coal+2*ore+4*copper+8*uranium) points, result
               FROM battleresults
              WHERE date > CURRENT_TIMESTAMP - INTERVAL '24' HOUR
                AND (coal+2*ore+4*copper+8*uranium) = (SELECT MAX(coal+2*ore+4*copper+8*uranium) points
                                                         FROM battleresults
                                                        WHERE date > CURRENT_TIMESTAMP - INTERVAL '24' HOUR)"""
    result = db.query(sql)
    loot_mission = None
    loot_attacker = None
    loot_defender = None
    date = None
    loot_points = None
    loot_result = None
    for row in result:
        loot_mission = row["mission_id"]
        loot_attacker = row["attacker"]
        loot_defender = row["defender"]
        loot_points = float(row["points"])
        loot_result = row["result"]
        date = int(row["date"].timestamp())

    response = {"loot_mission": loot_mission, "loot_attacker": loot_attacker,"loot_defender": loot_defender, "loot_date": date,"loot_points": loot_points, "loot_result": loot_result}

    return jsonify(response)

@app.route("/stardusttransfers", methods=['GET'])
def stardusttransfers():
    after_id = request.args.get('after_id', None)
    user = request.args.get('user',None)

    if user is None:
        return jsonify([])  
    if after_id is None:
        return jsonify([])     

    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    sql = """SELECT * FROM stardust WHERE id > """+after_id+""" AND (from_user = '"""+user+"""' OR to_user = '"""+user+"""') AND tr_type='transfer' ORDER BY id DESC"""
    result = db.query(sql)
    transaction_list = []
    for transaction in result:
        transaction["date"] = int(transaction["date"].timestamp())
        transaction_list.append(transaction)           

    if len(transaction_list) == 0:
        return jsonify([])

    return jsonify(transaction_list)

@app.route('/planetshipyard', methods=['GET'])
def planetshpiyard():
    planet = request.args.get('planet', None)
    user = request.args.get('user', None)
    name = request.args.get('name', None)

    if user is None:
        return jsonify([])
    if planet is None:
        return jsonify([])
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})

    table = db["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify([])
    battlespeed_buff = userdata["b_battlespeed"]
    apply_battlespeed = False
    if battlespeed_buff is not None:
        if battlespeed_buff > datetime.utcnow():
            apply_battlespeed = True

    if name is not None:
        name_condition = "full_table.name ='"+name+"'"
    else:
        name_condition = "1=1"
    sql=""" SELECT * FROM (
            SELECT *
            FROM shipstats shipstats
            INNER JOIN (SELECT name upgrade_type, coal, ore, copper, uranium, stardust, upgrade_time
            FROM upgradecosts) upgradecosts
            ON shipstats.name = upgradecosts.upgrade_type
            LEFT JOIN (SELECT type, MAX(busy_until) busy_until
            FROM ships
            WHERE user = '"""+user+"""'
             AND cords_hor IN (SELECT cords_hor from planets where id = '"""+planet+"""')
             AND  cords_ver IN (SELECT cords_ver from planets where id = '"""+planet+"""')
            GROUP BY type) ships
            ON shipstats.name = ships.type
            JOIN (SELECT level_shipyard, blueprints FROM planets where id = '"""+planet+"""') planets
            JOIN (SELECT r_shipyard, r_Explorer, r_Transporter, r_Scout, r_Patrol, r_Cutter, r_Corvette, r_Frigate, r_Destroyer, r_Cruiser, r_Battlecruiser, r_Carrier, r_Dreadnought, r_Yamato FROM users WHERE username = '"""+user+"""') users
            ) full_table WHERE """+name_condition+"""
        """
    result = db.query(sql)
    stack = []
    for row in result:
        if row["blueprint"] == 0:
            activated = True
        else:
            if row["blueprints"] is not None:
                if row["name"] in row["blueprints"]:
                    activated = True
                else:
                    activated = False
            else:
                activated = False
        ship_skill = row['r_' + row["class"]]
        if row["busy_until"] is not None:
            row["busy_until"] = int(row["busy_until"].timestamp())
        row["upgrade_time"] = row["upgrade_time"] * (1 - 0.01 * row["level_shipyard"]) # level_shipyard from planets

        basespeed = row["speed"]
        if apply_battlespeed:
            row["speed"] = row["battlespeed"]

        stack.append({
            "activated": activated,
            "type": row["name"],
            "speed": float(row["speed"]),
            "consumption": float(row["consumption"]),
            "longname": row["longname"],
            "capacity": int(row["capacity"]),
            "class": row["class"],
            "variant": row["variant_name"],
            "structure": int(row["structure"]),
            "armor": int(row["armor"]),
            "rocket": int(row["rocket"]),
            "bullet": int(row["bullet"]),
            "laser": int(row["laser"]),
            "busy_until": row["busy_until"],
            "blueprint": row["blueprint"],
            "costs": {"coal": row["coal"], "ore": row["ore"],"copper": row["copper"],"uranium": row["uranium"],"stardust": row["stardust"], "time": row["upgrade_time"]},
            "shipyard_level": row["level_shipyard"], # level_shipyard from planets
            "shipyard_skill": row["r_shipyard"],
            "shipyard_min_level": row["shipyard_level"],
            "ship_skill": ship_skill,
            "variant": row["variant"],
            "variant_name": row["variant_name"],
            "shield": row["shield"],
            "basespeed": basespeed,
            "battlespeed": row["battlespeed"],
            "order": row["order"]
        })

    return jsonify(stack)

@app.route('/missioninfo', methods=['GET'])
def missioninfo():
    planet = request.args.get('planet', None)
    user = request.args.get('user', None)

    if user is None:
        return jsonify({})
    if planet is None:
        return jsonify({})

    connection = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})

    table = connection["users"]
    userdata = table.find_one(username=user)
    if userdata is None:
        return jsonify({})
    missioncontrol = 0
    if userdata is not None:
        missioncontrol_buff = userdata["b_missioncontrol"] 
        if userdata["r_missioncontrol"] is not None:
            missioncontrol = userdata["r_missioncontrol"] 

    table = connection["planets"]
    planetdata = table.find_one(id=planet)
    if planetdata is None:
        return jsonify({})
    cords_hor = planetdata["cords_hor"]
    cords_ver = planetdata["cords_ver"]
    level_base = planetdata["level_base"]

    running_missions = 0
    table = connection["missions"]
    for mission in table.find(user=user, order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > datetime.utcnow():
            running_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > datetime.utcnow():
            running_missions += 1
    allowed_missions = missioncontrol * 2
    if missioncontrol_buff is not None and missioncontrol_buff > datetime.utcnow():
        allowed_missions = 400

    running_planet_missions = 0
    table = connection["missions"]
    for mission in table.find(user=user, cords_hor=cords_hor ,cords_ver=cords_ver,  order_by="-date"):
        if mission["busy_until_return"] is None and mission["busy_until"] > datetime.utcnow():
            running_planet_missions += 1
        elif mission["busy_until_return"] is not None and mission["busy_until_return"] > datetime.utcnow():
            running_planet_missions += 1
    allowed_planet_missions = math.floor(level_base / 2)

    user_unused = allowed_missions - running_missions
    planet_unused = allowed_planet_missions - running_planet_missions

    mission_allowed = False
    if planet_unused > 0 and user_unused > 0:
        mission_allowed = True

    response = {"user_max":allowed_missions,
                "user_active":running_missions,
                "planet_max":allowed_planet_missions,
                "planet_active":running_planet_missions,
                "user_unused": user_unused,
                "planet_unused": planet_unused,
                "mission_allowed": mission_allowed}

    return jsonify(response)    

@app.route('/buffs', methods=['GET'])
def buffs():
    user = request.args.get('user', None)
    if user is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    table = db["users"]
    userdata = table.find_one(username=user)
  
    if userdata is None:
        return jsonify([])
    
    table = db["buffs"]
    buffs = []
    for row in table.find():    
        buff_end = userdata["b_" + row["name"]]
        if buff_end is None:
            buff_end = 0
        else:
            buff_end = int(buff_end.timestamp())
            
        buffs.append({"name": row["name"], "price": row["price"], "buff_end": buff_end, "buff_duration": row["buff_duration"]})
       
    return jsonify(buffs)

@app.route('/yamatotracker', methods=['GET'])
def yamatotracker():
    yamato_list =[]
    now = datetime.utcnow()
    busy = request.args.get('busy', 2)
    upgrade = 0
    
    if busy is None:
        return jsonify([])
    
    db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
    if busy == "1":
        yamatodata = db.query('SELECT * FROM `ships` WHERE `type` LIKE "%yamato%" AND `mission_busy_until` > CURRENT_TIMESTAMP ORDER BY `ships`.`mission_busy_until` DESC')
    elif busy == "0":
        yamatodata = db.query('SELECT * FROM `ships` WHERE `type` LIKE "%yamato%" AND `mission_busy_until` < CURRENT_TIMESTAMP ORDER BY `ships`.`mission_busy_until` DESC')
    else:
        yamatodata = db.query('SELECT * FROM `ships` WHERE `type` LIKE "%yamato%" ORDER BY `ships`.`mission_busy_until` DESC')
        
    if yamatodata is None:
        return jsonify([])

    for ship in yamatodata:
        ship_type = ship['type']
        cords_hor = ship['cords_hor']
        cords_ver = ship['cords_ver']
        busy_until = ship['mission_busy_until']
        if busy_until > now:
            upgrade = 1
        else:
            upgrade = 0
        owner = ship['user']  
        busy_until = int(busy_until.timestamp())                            
        yamato_list.append({"type": ship_type, "cords_hor":cords_hor, "cords_ver":cords_ver, "owner": owner, "upgrade": upgrade, "upgrade_until": busy_until})
       
    return jsonify(yamato_list)


@app.route('/marketstats', methods=['GET'])
def marketstats():
    try:
        marketdata = {}
        db = dataset.connect(databaseConnector, engine_kwargs={'pool_recycle': 3600})
        
        data = db.query('SELECT COUNT(*) FROM `asks` WHERE `category` = "ship" AND `sold` IS NULL AND `cancel_trx` IS NULL' )
        for row in data:
            ships_on_market = int(row['COUNT(*)'])
        
        data = db.query('SELECT COUNT(*) FROM `asks` WHERE `category` = "planet" AND `sold` IS NULL AND `cancel_trx` IS NULL ')
        for row in data:
            planets_on_market = int(row['COUNT(*)'])
            
        data = db.query('SELECT COUNT(*) FROM `asks` WHERE `category` = "item" AND `sold` IS NULL AND `cancel_trx` IS NULL ')
        for row in data:
            items_on_market = int(row['COUNT(*)'])
        
        data = db.query('SELECT COUNT(*) FROM `asks` WHERE `sold` IS NOT NULL')
        for row in data:
            transaction_number = int(row['COUNT(*)'])
        data = db.query('SELECT SUM(price) FROM `asks` WHERE `sold` IS NOT NULL')
        for row in data:
            trading_volume = int(row['SUM(price)'])
        
        data = db.query('SELECT SUM(fee_burn) FROM `asks` WHERE `sold` IS NOT NULL')
        for row in data:
            total_fee_burned = int(row['SUM(fee_burn)'])
        
        data = db.query('SELECT SUM(amount) FROM `stardust` WHERE `tr_type` = "market" AND `to_user` = "null" LIMIT 1 ')
        for row in data:
            total_sent_null = int(row['SUM(amount)'])
        total_burned = total_sent_null + total_fee_burned
        
        data = db.query('SELECT * FROM `asks` WHERE `sold` IS NOT NULL ORDER BY `price` DESC LIMIT 1')
        for row in data:
            product_type = row['type']
            category = row['category']
            seller = row['user']
            price = int(row['price'])
            highest_sale = {"type": product_type, "category": category, "seller":seller, "price":price}      
        marketdata = {"planets_on_market":planets_on_market, "ships_on_market":ships_on_market, "items_on_market":items_on_market, "transaction_number": transaction_number, "trading_volume":trading_volume, "total_burned":total_burned, "highest_sale":highest_sale }
        return jsonify(marketdata)
    except:
        return jsonify([])
        


if __name__ == '__main__':
    app.run()
