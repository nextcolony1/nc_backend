import json
import time
import datetime
import os
from datetime import timedelta, datetime
import requests
import logging
from beem.blockchain import Blockchain
from beem.block import Block
from beem.amount import Amount
import dataset
from beem import Steem
from beem.nodelist import NodeList
from utils.ncutils import get_custom_json_id, get_transfer_id
from unidecode import unidecode

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)
log.setLevel(logging.ERROR)

def read_config():
    config_file = 'config.json'
    if not os.path.isfile(config_file):
        raise Exception("config.json is missing!")
    else:
        with open(config_file) as json_data_file:
            config_data = json.load(json_data_file)
    return config_data

def get_latest_block_num():
    config_data = read_config()
    databaseConnector = config_data["databaseConnector"]
    start_block_num = 32247771
    db = dataset.connect(databaseConnector)
    table = db['transactions']
    latest_entry = table.find_one(order_by='-block_num', virtualop=0)
    if latest_entry is None:
        latest_block_num = start_block_num
    elif "block_num" not in latest_entry:
        latest_block_num = start_block_num
    else:
        latest_block_num = latest_entry["block_num"]
    if latest_block_num is None:
        latest_block_num = start_block_num
    if latest_block_num == start_block_num:
        table = db['status']
        table.upsert({"id": 1, "start_block_num": start_block_num, "latest_block_num": start_block_num}, ["id"])
    db.executable.close()
    return latest_block_num

def print_block_log(start_block_num, log_data, block_num, timestamp):
    start_time = log_data["start_time"]
    last_block_num = log_data["last_block_num"]
    new_custom_json = log_data["new_custom_json"]
    new_transfers = log_data["new_transfers"]
    stop_block_num = log_data["stop_block_num"]
    time_for_blocks = log_data["time_for_blocks"]
    print_log_at_block_diff = log_data["print_log_at_block_diff"]
    
    if last_block_num is None:
        start_time = time.time()
        last_block_num = block_num
        new_custom_json = 0
        new_transfers = 0
    if (block_num - last_block_num) > print_log_at_block_diff:
        time_for_blocks = time.time() - start_time
        if print_log_at_block_diff > 200 and (stop_block_num - start_block_num) > 0:
            percentage_done = (block_num - start_block_num) / (stop_block_num - start_block_num) * 100
            print("Block %d -- Datetime %s -- %.2f %% finished" % (block_num, timestamp, percentage_done))
            running_hours = (stop_block_num - block_num) * time_for_blocks / print_log_at_block_diff / 60 / 60
            print("Duration for %d blocks: %.2f s (%.3f s per block) -- %.2f hours to go" % (print_log_at_block_diff, time_for_blocks, time_for_blocks / print_log_at_block_diff, running_hours))
        else:
            print("Block %d -- Datetime %s" % (block_num, timestamp))
        print("%d  new nextcolony custom_json" % new_custom_json)
        print("%d  new nextcolony transfers" % new_transfers)
        start_time = time.time()
        new_custom_json = 0
        new_transfers = 0
        last_block_num = block_num
    log_data["start_time"] = start_time
    log_data["last_block_num"] = last_block_num
    log_data["new_custom_json"] = new_custom_json
    log_data["time_for_blocks"] = time_for_blocks
    return log_data
    

def get_transactions(start_block_num, log_data):
    config_data = read_config()
    databaseConnector = config_data["databaseConnector"]    
    custom_json_id = config_data["custom_json_id"]
    transfer_id = config_data["transfer_id"]
    
    current_block = start_block_num - 1
    
    nodes = NodeList()
    # weights = {'block': 1, 'history': 0.5, 'apicall': 0.5, 'config': 0.5}
    nodes.update_nodes()
    stm = Steem(node=["https://api.steemit.com"])    
    print(stm)
    
    b = Blockchain(mode="head", steem_instance=stm)
    if "stop_block_num" in config_data and config_data["stop_block_num"] > 0:
        stop_block_num = config_data["stop_block_num"]
    else:
        stop_block_num = b.get_current_block_num()
    if stop_block_num - start_block_num > 1200:
        stop_block_num = start_block_num + 1200
    log_data["stop_block_num"] = stop_block_num 
        
    db = dataset.connect(databaseConnector)
    
    table = db['status']
    table.upsert({"id": 1, "tracker_stop_block_num": stop_block_num}, ["id"])     
    
    table = db["blocks"]
    data = table.find_one(order_by='-block_num')
    if data is None:
        latest_block_num = start_block_num - 1
    else:
        latest_block_num = data["block_num"]
        
    table = db["virtualops"]
    for block in b.blocks(start=start_block_num, stop=stop_block_num, threading=False, thread_num=8):
        if "transactions" in block:
            trx = block["transactions"]
        else:
            trx = [block]
        block_num = 0
        trx_id = ""
        _id = ""
        timestamp = ""
        for trx_nr in range(len(trx)):
            if "operations" not in trx[trx_nr]:
                continue
            for event in trx[trx_nr]["operations"]:
                if isinstance(event, list):
                    op_type, op = event
                    trx_id = block["transaction_ids"][trx_nr]
                    block_num = block.get("id")
                    timestamp = block.get("timestamp")
                    block_id = block.get("block_id")
                    previous = block.get("previous")
                elif isinstance(event, dict) and "type" in event and "value" in event:
                    op_type = event["type"]
                    if len(op_type) > 10 and op_type[len(op_type) - 10:] == "_operation":
                        op_type = op_type[:-10]
                    op = event["value"]
                    trx_id = block["transaction_ids"][trx_nr]
                    block_num = block.get("id")
                    timestamp = block.get("timestamp")
                    block_id = block.get("block_id")
                    previous = block.get("previous")                    
                elif "op" in event and isinstance(event["op"], dict) and "type" in event["op"] and "value" in event["op"]:
                    op_type = event["op"]["type"]
                    if len(op_type) > 10 and op_type[len(op_type) - 10:] == "_operation":
                        op_type = op_type[:-10]
                    op = event["op"]["value"]
                    trx_id = event.get("trx_id")
                    block_num = event.get("block")
                    timestamp = event.get("timestamp")
                    block_id = None
                    previous = None
                else:
                    op_type, op = event["op"]
                    trx_id = event.get("trx_id")
                    block_num = event.get("block")
                    timestamp = event.get("timestamp")
                    block_id = None
                    previous = None                    
        
        
                # print(op)
                log_data = print_block_log(start_block_num, log_data, block_num, timestamp)
                current_block = block_num
                date = timestamp.replace(tzinfo=None)        
                if block_num > latest_block_num:
                    table = db["blocks"]
                    table.insert({"block_num": block_num, "timestamp": date, "block_id": block_id, "previous": previous})
                    latest_block_num = block_num
                if op_type == "transfer":
                    if op["to"] != "nextcolony":
                        continue
                    user = op["from"]
                    memo = op["memo"]
                    at_symbol_pos = memo.find('@')
                    if at_symbol_pos < 0:
                        continue
                    if memo[:at_symbol_pos] != transfer_id:
                        continue
                    amount = Amount(op["amount"], steem_instance=stm)
        
                    log_data["new_transfers"] += 1
                    table = db['transfers']
                    if table.find_one(trx=trx_id) == None:
                        print ("Writing the transaction into the DB")
                        data = dict(trx=trx_id, user=user, block_num=int(block_num), amount=str(amount), memo=memo, tr_status=0, date=date)
                        table.insert(data)
                        table = db['status']
                        table.upsert({"id": 1, "latest_block_num": int(block_num)}, ["id"])                
                elif op_type == "custom_json":
                    if op['id'] != custom_json_id:
                        continue
                    
                    date = timestamp.replace(tzinfo=None)
        
                    try:
                        json_data = json.loads(op['json'])
                    except:
                        print("Skip json: %s" % str(op['json']))
                        continue
                    
                    
                    if isinstance(json_data, list) and len(json_data) == 1:
                        json_data = json_data[0]
                    if not isinstance(json_data, dict):
                        print(json_data)
                        print("not a valid json")
                        continue
        
                    if 'command' not in json_data:
                        print (json_data)
                        print("wrong cusom_json structure")
                        continue
                    if len(json_data['command']) == 0:
                        print(json_data)
                        print("command is empty")
                        continue
                    if len(op['required_posting_auths']) > 0:
                        user = op['required_posting_auths'][0]
                    elif len(op['required_auths']) > 0:
                        user = op['required_auths'][0]
                    else:
                        print("Cannot parse transaction, as user could not be determined!")
                        continue
                    table = db['transactions']            
                    if table.find_one(trx=trx_id) != None:
                        print("Skip trx_id %s at %s" % (trx_id, date))
                        continue
                    log_data["new_custom_json"] += 1
                    command = json_data['command']
                    if "type" not in json_data:
                        continue
                    if json_data["type"] is None:
                        continue
                    json_type = json_data['type']

                    print("%s: %d:%s - @%s type: %s, command: %s" % (str(date), block_num, trx_id, user, str(json_type), str(command)))
  
                    if not isinstance(command, dict):
                        print("Skip trx_id %s at %s" % (trx_id, date))
                        continue                
                    if "tr_var1" in command:
                        tr_var1 = unidecode(str(command['tr_var1']))
                    else:
                        tr_var1 =  0
                    if "tr_var2" in command:
                        tr_var2 = unidecode(str(command['tr_var2']))
                    else:
                        tr_var2 =  0            
                    if "tr_var3" in command:
                        tr_var3 = unidecode(str(command['tr_var3']))
                    else:
                        tr_var3 =  0
                    if "tr_var4" in command:
                        tr_var4 = unidecode(str(command['tr_var4']))
                    else:
                        tr_var4 =  0
                    if "tr_var5" in command:
                        tr_var5 = unidecode(str(command['tr_var5']))
                    else:
                        tr_var5 =  0
                    if "tr_var6" in command:
                        tr_var6 = unidecode(str(command['tr_var6']))
                    else:
                        tr_var6 =  0
                    if "tr_var7" in command:
                        tr_var7 = unidecode(str(command['tr_var7']))
                    else:
                        tr_var7 =  0
                    if "tr_var8" in command:
                        tr_var8 = unidecode(str(command['tr_var8']))
                    else:
                        tr_var8 =  0                            
                
                    table = db['transactions']
                    data = dict(trx=trx_id, user=user, tr_type=json_type, block_num=int(block_num), tr_var1=str(tr_var1),
                                tr_var2=str(tr_var2), tr_var3=tr_var3, tr_var4=tr_var4, tr_var5=tr_var5,
                                tr_var6=tr_var6, tr_var7=tr_var7, tr_var8=tr_var8, tr_status=0 ,date=date)
                    table.insert(data)
                    table = db['status']
                    table.upsert({"id": 1, "latest_block_num": int(block_num)}, ["id"])            
    
    return current_block + 1, log_data

if __name__ == '__main__':
    start_block_num = get_latest_block_num()
    if start_block_num is not None:
        print("Start to stream at block %d" % start_block_num)
    else:
        print("Start to stream from beginning")
    
    log_data = {"start_time": 0, "last_block_num": None, "new_custom_json": 0, "new_transfers": 0, "stop_block_num": 0, "time_for_blocks": 0, "print_log_at_block_diff": 1200} 
    repeat_count = 0
    while repeat_count < 28800:
        repeat_count += 1
        if True:
            start_block_num, log_data = get_transactions(start_block_num, log_data)
            # Switch log to 5 min distance
            log_data["print_log_at_block_diff"] = 100
            time.sleep(3)
