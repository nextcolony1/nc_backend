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
from fix_data import fix_data


 

if __name__ == '__main__':
    time_now = datetime.utcnow()
    connection = connectdb()
    fix_data(time_now, None, test_mode=True)