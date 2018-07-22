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
                    password TEXT
                    );""")

    def login(self, username, password):
        cmd = """SELECT account_id FROM Accounts WHERE username = ? AND password = ?"""
        data = ''
        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd, (username, password))
            data = self.cur.fetchone()
        finally:
            self.thread_lock.release()


        if data != None:
            return True
        else:
            return False

    def create_account(self, first, last, username, password):

        cmd = """INSERT INTO Accounts(first_name, last_name, username, password) VALUES(?,?,?,?)"""

        try:
            self.thread_lock.acquire(True)
            self.cur.execute(cmd, (first, last, username, password))
            self.conn.commit()
        finally:
            self.thread_lock.release()

        self.create_table(username)

    def create_table(self, username):
        cmd = """CREATE TABLE {}(
            routine_number INTEGER PRIMARY KEY ,
            routine_name TEXT,
            departure_time INTEGER,
            start_location TEXT,
            end_location TEXT
            );""".format(username)

        try:
            self.thread_lock.acquire(True)
            self.cur.executescript(cmd)
            self.conn.commit()
        finally:
            self.thread_lock.release()

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
