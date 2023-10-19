import sqlite3
from sqlite3 import Error

DATABASE_PATH = "./"

#######################################################
### :desc: create a database connection to the SQLite
###        database specified by db_file.
### :param db_file: database file
### :return: Connection object or None
#######################################################
def create_connection(db_file):
    conn = None
    db_file = DATABASE_PATH + "/" + db_file
    try:
        conn = sqlite3.connect(db_file)
        create_database(db_file, conn)
        return conn
    except Error as e:
        print(e)

    return conn


#######################################################
### :desc: create a table from the create_table_sql 
###        statement.
### :param conn: Connection object
### :param create_table_sql: a CREATE TABLE statement
### :return: None
#######################################################
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


#######################################################
### :desc: create database and database file if it not
###        exists.
### :param DATABASE: file
### :param conn: Connection object
### :return: None
#######################################################
def create_database(DATABASE, conn = None):
    sql_bus_info_table = """ CREATE TABLE IF NOT EXISTS info (
                                id VARCHAR(32),
                                lat FLOAT,
                                lon FLOAT,
                                speed int,
                                timestamp int,
                                is_proved BOOLEAN,

                                CONSTRAINT PK_info PRIMARY KEY (id, timestamp)
                            ); """

    close_at_end = False
    # create a database connection
    if conn is None:
        conn = create_connection(DATABASE)
        close_at_end = True

    # create tables
    if conn is not None:
        
        # create info table
        create_table(conn, sql_bus_info_table)

        if close_at_end: conn.close()
    else:
        print("Error! cannot create the database connection.")


###################################################################
#                                                                 #
#                         AUX FUNCTIONS                           #
#                                                                 #
###################################################################
def str_to_coords(coords_str:str):
    coords = coords_str.split(";")

    for i in range(len(coords)):
        coords[i] = list(map(float, coords[i].split(",")))
    
    return coords

def list_to_str(my_list:list):
    s = ""
    if type(my_list[0]) == list: # coordinates list: [[lat0, lon0], [lat1, lon1],...]
        for coord in my_list:
            s += f"{coord[0]},{coord[1]};" # lat0,lon1;lat1,lon1;lat2,lon2
    else: # schedule list: ['07:45:0', '07:46:0',...]
        for ts in my_list:
            s += f"{ts};"
    
    return s[:-1] # remove last ";"


###################################################################
#                                                                 #
#                            INSERTS                              #
#                                                                 #
###################################################################
def insert_info(conn, id, lat, lon, spd, ts):
    sql = '''INSERT OR REPLACE INTO info (id, lat, lon, speed, timestamp, is_proved)
              VALUES(?, ?, ?, ?, ?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (id, lat, lon, spd, ts, False))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    return True


###################################################################
#                                                                 #
#                            QUERIES                              #
#                                                                 #
###################################################################

def select_info(conn, bus_id, ts):
    sql = '''SELECT id, lat, lon, timestamp FROM info WHERE id = ? AND timestamp = ?'''
    cur = conn.cursor()
    cur.execute(sql, (bus_id, ts))

    return cur.fetchone()

def select_bus_cord(conn, bus_id):
    sql = '''SELECT lat, lon, id FROM info WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (bus_id,))

    return cur.fetchone()

def select_ng (conn, id, ts):
    sql = '''SELECT id,lat,lon FROM info WHERE timestamp = ? AND id != ? '''
    cur = conn.cursor()
    cur.execute(sql, (ts, id))


    return cur.fetchall() # fetchall = [(id0,lat0,lon0,), (id1,,lat0,lon0,), (id2,,lat0,lon0,), ...]

def select_last(conn, bus_id, ts):
    sql = '''SELECT lat, lon, speed, MAX(timestamp) FROM info WHERE id = ? AND timestamp < ? AND is_proved = ? '''
    cur = conn.cursor()
    cur.execute(sql, (bus_id, ts, True))

    return cur.fetchone()

###################################################################
#                                                                 #
#                            UPDATES                              #
#                                                                 #
###################################################################
def set_proved(conn, id, ts):
    sql = ''' UPDATE info SET is_proved = ? WHERE id = ? AND timestamp = ? '''
    cur = conn.cursor()
    cur.execute(sql, (True, id, ts))

    return cur.fetchall()

if __name__ == "__main__":
    create_database("schedules.db", None)