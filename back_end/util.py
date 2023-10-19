import math
import datetime

DIST_TOLERANCE = 0.05 # km


def str_to_eth_hex(s):
    hex = "0x" + s.encode('utf-8').hex()
    return hex

def hex_to_str(hex):
    if hex[:2] == '0x':
        hex = hex[2:]
    string_value = bytes.fromhex(hex).decode('utf-8')
    return string_value

def hex_to_bin(hex):
    return bin(int(hex, base=16))[2:]


# distance between two GPS coordinates. Return distance in KM
def distance_between_coordinates(lat1, lon1, lat2, lon2):
    earthRadiusKm = 6371

    dLat = (lat2-lat1) * math.pi / 180
    dLon = (lon2-lon1) * math.pi / 180

    lat1 = (lat1) * math.pi / 180
    lat2 = (lat2) * math.pi / 180

    a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2) 
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return earthRadiusKm * c


def in_route(lat, lon, route):
    min_distance = None # minimum distance from route
    for r_coord in route:
        r_lat, r_lon = r_coord
        distance = distance_between_coordinates(lat, lon, r_lat, r_lon)
        if distance <= DIST_TOLERANCE:
            return True
        
        if min_distance is None or min_distance > distance:
            min_distance = distance
    
    return min_distance


def is_late(curr_time, stop_time):
    #curr_time = "%Y-%m-%d %H:%M:%S"
    #stop_time = "%H:%M:%S"
    curr_hour = curr_time.split(" ")[1]
    curr_datetime = datetime.datetime.strptime(curr_hour, "%H:%M:%S")
    stop_datetime = datetime.datetime.strptime(stop_time, "%H:%M:%S")

    if curr_datetime > stop_datetime:
        #return True
        return curr_datetime - stop_datetime
    
    return False
    
    
def next_stop(lat, lon, stops):
    for r_coord in stops:
        r_lat, r_lon, r_id = r_coord
        if distance_between_coordinates(lat, lon, r_lat, r_lon) <= DIST_TOLERANCE:
            return r_id
    
    return None
