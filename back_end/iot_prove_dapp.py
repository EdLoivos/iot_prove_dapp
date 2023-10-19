# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from os import environ
import logging
import requests

import json
import db_manager as db
import graph_manager as gm
import util

DB_FILE = "schedules.db"
GR_FILE = "neighbors.json"

REACH = 1

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")


def handle_advance(data):
    try:
        #logger.info(f"Received advance request data {data}")

        ### payload to UTF-8
        payload_utf8 = util.hex_to_str(data["payload"])
        # logger.info(f"Payload UTF-8 {payload_utf8}")

        ### managing database
        conn = db.create_connection(DB_FILE)
        ng_dict = gm.loadConect(GR_FILE)

        try:
            payload_dict = json.loads(payload_utf8)
        except json.decoder.JSONDecodeError:
            conn.close()
            return "reject"

        #### receiving GPS entry
        bus_id = payload_dict["bus_id"] #Bus unique id
        curr_lat = payload_dict["lat"] #Latitude
        curr_lon = payload_dict["lon"] #Longitude
        spd = payload_dict["spd"] #Speed
        ts = int(payload_dict["ts"]) #Timestamp
        ng = payload_dict["ng"] #Neighbors
        db.insert_info(conn, bus_id, curr_lat, curr_lon, spd, ts)


        if str(ts) not in ng_dict: ng_dict[str(ts)] = {}
        
        # search for buses near the declared position
        curr_near = []
        for l in db.select_ng(conn, bus_id, ts):
            if util.distance_between_coordinates(l[1], l[2], curr_lat,curr_lon) <= REACH:
                curr_near.append(l[0])
        if str(bus_id) in ng_dict[str(ts)]:
            
            curr_seen = ng_dict[str(ts)][str(bus_id)]
        else:
            curr_seen = []



        total_points =  list(set(curr_near+curr_seen))
        tp =  list(set(curr_near).intersection(curr_seen))     
        if(len(total_points)>=3):
            
            if(len(tp)>= len(total_points)/2):
                prov_dsc = {
                        "ts": ts,
                        "tp": 3,
                        "bus_line": bus_id,
                        "stat": "Confirmed",
                        "ng": total_points,
                        "ng_ap": tp,
                        "curr_coords": (curr_lat, curr_lon),
                        "value": "list"
                    }
                
                db.set_proved(conn, bus_id, ts)
            else:
                prov_dsc = {
                        "ts": ts,
                        "tp": 3,
                        "bus_line": bus_id,
                        "stat": "Warn",
                        "ng": total_points,
                        "ng_ap": tp,
                        "curr_coords": (curr_lat, curr_lon),
                        "value": "list"
                    }
            if prov_dsc:
                    notice_payload = util.str_to_eth_hex(json.dumps(prov_dsc))
                    logger.info("### Notice Payload ###")
                    logger.info(notice_payload)
                    logger.info("### Notice Payload ###")
                    logger.info("Adding notice")
                    response = requests.post(rollup_server + "/notice", json={ "payload": notice_payload })
                    logger.info(f"Received notice status {response.status_code} body {response.content}")
        else:
            #formula check
            last_lat, last_lon, start_spd, last_ts = db.select_last(conn, bus_id, ts)
            if last_lat is not None and last_lon is not None and start_spd is not None and last_ts is not None:
                delta_t = (ts + 0.5) - last_ts 
                max_acc = 2.81
                min_acc = -8.54
                max_dist = (start_spd/3.6*delta_t + (max_acc* pow(delta_t, 2))/2)/1000
                min_dist = (start_spd/3.6*delta_t + (min_acc* pow(delta_t, 2))/2)/1000
                delta_s = util.distance_between_coordinates(curr_lat, curr_lon, last_lat, last_lon)
                if delta_s >= min_dist and delta_s <= max_dist:
                    prov_dsc = {
                            "ts": ts,
                            "tp": 4,
                            "bus_line": bus_id,
                            "stat": "Confirmed",
                            "last_prov_ts": last_ts,
                            "curr_coords": (curr_lat, curr_lon),
                            "value": "list"
                        }

                    db.set_proved(conn, bus_id, ts)
                    
                else:
                    prov_dsc = {
                            "ts": ts,
                            "tp": 4,
                            "bus_line": bus_id,
                            "stat": "Warn",
                            "last_prov_ts": last_ts,
                            "curr_coords": (curr_lat, curr_lon),
                            "value": "list"
                        }
                if prov_dsc:
                        notice_payload = util.str_to_eth_hex(json.dumps(prov_dsc))
                        logger.info("### Notice Payload ###")
                        logger.info(notice_payload)
                        logger.info("### Notice Payload ###")
                        logger.info("Adding notice")
                        response = requests.post(rollup_server + "/notice", json={ "payload": notice_payload })
                        logger.info(f"Received notice status {response.status_code} body {response.content}")
        #ok
        for obj in ng:
            if str(obj) in ng_dict[str(ts)]:
                if str(bus_id) not in ng_dict[str(ts)][str(obj)]:
                    ng_dict[str(ts)][str(obj)].append(str(bus_id))
            else:
                ng_dict[str(ts)][str(obj)] = [str(bus_id)]
            
            tg_info = db.select_info(conn, obj, ts)
            if tg_info != None:
                obj_id = tg_info[0]
                obj_lat = tg_info[1]
                obj_lon = tg_info[2]

                curr_near = []
                for l in db.select_ng(conn, obj_id, ts):
                    if util.distance_between_coordinates(l[1], l[2], obj_lat, obj_lon) <= REACH:
                        curr_near.append(l[0])

                curr_seen = ng_dict[str(ts)][str(obj_id)]
                tp =  list(set(curr_near).intersection(curr_seen))        
                if(len(tp)>=3):
                    total_points =  list(set(curr_near+curr_seen))
                    if(len(tp)>= len(total_points)/2):
                        prov_dsc = {
                                "ts": ts,
                                "tp": 3,
                                "bus_line": obj_id,
                                "stat": "Confirmed",
                                "ng": total_points,
                                "ng_ap": tp,
                                "curr_coords": (obj_lat, obj_lon),
                                "value": "list"
                            }
                    else:
                        prov_dsc = {
                                "ts": ts,
                                "tp": 3,
                                "bus_line": obj_id,
                                "stat": "Warn",
                                "ng": total_points,
                                "ng_ap": tp,
                                "curr_coords": (obj_lat, obj_lon),
                                "value": "list"
                            }
                    if prov_dsc:
                            notice_payload = util.str_to_eth_hex(json.dumps(prov_dsc))
                            logger.info("### Notice Payload ###")
                            logger.info(notice_payload)
                            logger.info("### Notice Payload ###")
                            logger.info("Adding notice")
                            response = requests.post(rollup_server + "/notice", json={ "payload": notice_payload })
                            logger.info(f"Received notice status {response.status_code} body {response.content}")
                else:
                    #formula check
                    pass         
        
        gm.saveConect(ng_dict,GR_FILE)
        
        conn.close()
        return "accept"
    except Exception as e:
        logger.info(f"Unexpected Error: {e}\nRejecting...")
        conn.close()
        return "reject"

def handle_inspect(data):
    try:
        ### payload to UTF-8
        payload_utf8 = util.hex_to_str(data["payload"])
        logger.info(f"Inspect Payload UTF-8 {payload_utf8}")

        payload_dict = json.loads(payload_utf8)
        logger.info(f"Payload DICT {payload_dict}")

        def generate_report(msg):
            result = util.str_to_eth_hex(msg)
            logger.info("Adding report")
            response = requests.post(rollup_server + "/report", json={"payload": result})
            logger.info(f"Received report status {response.status_code}")


        if "select" not in payload_dict:
            generate_report(f"Must have 'select' key! Valid values are: {list(select_options.keys())}")
            return "reject"

            
        conn = db.create_connection(DB_FILE)
        option = payload_dict["select"]
        select_options = {
            "neighbors": {"required": True, "time": True, "function": db.select_bus_cord },
            "position": {"required": True, "time": True, "function": db.select_info }
        }
        

        if option not in select_options:
            generate_report(f"Invalid select option! Valid options are: {list(select_options.keys())}")
            return "reject"


        select_function = select_options[option]["function"]
        if not select_options[option]["required"]:
            result = select_function(conn)
        else:
            if option not in payload_dict:
                generate_report(f"Missing key: {option}")
                return "reject"

            option_value = payload_dict[option]
            if type(option_value) == str:
                if select_options[option]["time"]:                    
                    result = select_function(conn, option_value, payload_dict["time"])
                else:
                    result = select_function(conn, option_value)
            elif type(option_value) == list:
                result = {}
                for val in option_value:
                    if select_options[option]["time"]:         
                        result[val] = select_function(conn, val, payload_dict["time"])
                    else:
                        result[val] = select_function(conn, val)
            else:
                generate_report(f"{option} value must be a list or a string!")
                return "reject"
                
        print(result)
        generate_report(json.dumps(result))
        return "accept"
    
    except Exception as e:
        logger.info(f"Unexpected Error: {e}\nRejecting...")
        return "reject"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
rollup_address = None

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        metadata = rollup_request["data"].get("metadata")
        if metadata and metadata["epoch_index"] == 0 and metadata["input_index"] == 0:
            rollup_address = metadata["msg_sender"]
            logger.info(f"Captured rollup address: {rollup_address}")
        else:
            handler = handlers[rollup_request["request_type"]]
            finish["status"] = handler(rollup_request["data"])
