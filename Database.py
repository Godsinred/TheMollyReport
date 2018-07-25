import requests
import pprint
import sqlite3
import getpass
import sys


KEY = "AIzaSyB_R-OTY2BwfqtjqWQ3eBPRfoTb8WywqFU"
DAY = 86400 # amount of seconds in a day
URL = "https://maps.googleapis.com/maps/api/directions/json"

class Database():
    def __init__(self, thread_lock):
        self.conn = sqlite3.connect("everything_db.sqlite", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.thread_lock = thread_lock

        self.cur.executescript("""CREATE TABLE IF NOT EXISTS Accounts(
                    account_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    password TEXT,
                    thread_id TEXT,
                    thread_type TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS Routes(
                    route_number INTEGER PRIMARY KEY,
                    route_name TEXT,
                    departure_time INTEGER,
                    start_location TEXT,
                    end_location TEXT,
                    username TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS Times(
                    time INTEGER UNIQUE);""")

    def login(self, username, password):
        cmd = "SELECT account_id FROM Accounts WHERE username = \'{}\' AND password = \'{}\'".format(username, password)
        data = ''
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd)
            data = self.cur.fetchone()
        finally:
            self.thread_lock.release()


        if data != None:
            return True
        else:
            return False

    def create_account(self, first, last, username, password, thread_id, thread_type):

        cmd = """INSERT INTO Accounts(first_name, last_name, username, password, thread_id, thread_type) 
                VALUES(?,?,?,?,?,?)"""

        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd, (first, last, username, password, thread_id, thread_type))
            self.conn.commit()
        finally:
            self.thread_lock.release()

        try:
            self.thread_lock.acquire(True)
            self.cur.executescript(cmd)
            self.conn.commit()
        finally:
            self.thread_lock.release()

    def get_all_routes(self, username):
        cmd = """SELECT * FROM Routes WHERE username = \'{}\'""".format(username)
        data = []
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd)
            data = self.cur.fetchall()
        finally:
            self.thread_lock.release()
        print(data)
        return data

    def create_route(self, start, end, time, name, username):
        cmd = """INSERT INTO Routes(route_name, departure_time, start_location, end_location, username) 
                VALUES(?,?,?,?,?)"""

        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd, (name, time, start, end, username))
            self.conn.commit()
            self.cur.execute("INSERT INTO Times(time) VALUES(?)", (time,))
            self.conn.commit()
        finally:
            self.thread_lock.release()

    def get_routes_with_time(self, time):
        cmd = """SELECT * from Routes WHERE departure_time={}""".format(time)
        user_info_list = []
        routes = []
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd)
            routes = self.cur.fetchall()
            username_list = []
            for name in routes:
                if name[5] not in username_list:
                    username_list.append(name[5])

            for name in username_list:
                self.cur.execute("""SELECT first_name, username, thread_id, thread_type FROM Accounts
                                WHERE username = \'{}\'""".format(name))
                info = self.cur.fetchone()
                user_info_list.append(info)

        finally:
            self.thread_lock.release()

        return (routes, user_info_list)

    def update_route(self, username, route_number, route_update, route_info):
        cmd = "SELECT route_number from Routes WHERE username=\'{}\'".format(username)
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd)
            routes = self.cur.fetchall()
            route = routes[int(route_number) - 1][0]

            if route_update == 1:
                cmd = "UPDATE Routes SET route_name=\'{}\' WHERE route_number = {}".format(route_info, route)
            elif route_update == 2:
                self.cur.execute("INSERT INTO Times(time) VALUES(?)", (int(route_info),))
                self.conn.commit()
                cmd = "UPDATE Routes SET departure_time={} WHERE route_number = {}".format(int(route_info), route)
            elif route_update == 3:
                cmd = "UPDATE Routes SET start_location=\'{}\' WHERE route_number = {}".format(route_info.replace(' ', '+'), route)
            elif route_update == 4:
                cmd = "UPDATE Routes SET end_location=\'{}\' WHERE route_number = {}".format(route_info.replace(' ', '+'), route)

            self.cur.execute(cmd)
            self.conn.commit()
        finally:
            self.thread_lock.release()

    def delete_route(self, username,  route_number):
        cmd = "SELECT route_number FROM Routes WHERE username=\'{}\'".format(username)
        route_name = ''
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd)
            routes = self.cur.fetchall()
            route_num = routes[int(route_number) - 1][0]

            cmd = "SELECT route_name FROM Routes WHERE route_number={}".format(route_num)
            self.cur.execute(cmd)
            route_name = self.cur.fetchone()[0]

            cmd = "DELETE FROM Routes WHERE route_number={}".format(route_num)
            self.cur.execute(cmd)
            self.conn.commit()
        finally:
            self.thread_lock.release()

        return route_name

    def route_info(self):
        origin = "1334+Spectrum+Irvine+CA"
        destination = "475+Anton+Blvd+Costa+Mesa+CA"

        # optional parameters departure_time and arrival time since midnight, January 1, 1970 UTC

        departure = 1530288000 # friday 6/29 at 9am

        query = {"key" : KEY, "destination" : destination, "origin" : origin, "avoid" : "tolls", "departure_time" : "now", "traffic_model" : "best_guess"}
        r = requests.get(URL, params=query)
        info = r.json()

        # pp = pprint.PrettyPrinter(indent = 4)
        # pp.pprint(info)
        print("URL: " + r.url)

        if info["status"] == "OK":
            print("Distance: " +  info["routes"][0]["legs"][0]["distance"]["text"])
            print("Duration in Traffic: " +  info["routes"][0]["legs"][0]["duration_in_traffic"]["text"])
        else:
            print("status != OK")

        print()

        route = []
        for step in info["routes"][0]["legs"][0]["steps"]:
            inst = step["html_instructions"]
            present = True
            while present:
                start = inst.find('<')
                if start >= 0:
                    end = inst.find('>')
                    inst = inst[:start].strip() + ' ' + inst[end+1:].strip()
                    print(inst)
                else:
                    present = False
            route.append(inst)

        print(route)
