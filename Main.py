import requests
import pprint
import sqlite3
import getpass
import sys
import FacebookMessage


KEY = "AIzaSyB_R-OTY2BwfqtjqWQ3eBPRfoTb8WywqFU"
DAY = 86400 # amount of seconds in a day
URL = "https://maps.googleapis.com/maps/api/directions/json"

# def login(cur):
#     username = input("Enter your username: ")
#     pw = getpass.getpass(prompt="Enter your password: ", stream=None)
#
#     cur.execute("""SELECT account_id FROM Accounts
#     WHERE username = ? AND password = ?""", (username, pw))
#
#     data = cur.fetchone()
#     if data != None:
#         return True
#     else:
#         return False
#
# def create_account(conn, cur):
#     first = input("Enter in first name: ")
#     last = input("Enter in last name: ")
#     username = input("Enter in username: ")
#     pw = input("Enter in password: ")
#
#     cur.execute("SELECT username FROM Accounts")
#     all_usernames = cur.fetchall()
#     if username in all_usernames:
#         print("Username: \"{}\" is already taken. Please choose a new username.".format(username))
#         while username in all_usernames:
#             username = input("New username: ")
#
#     cur.execute("""INSERT INTO Accounts(first_name, last_name, username, password) VALUES(?,?,?,?)""", (first, last, username, pw))
#     conn.commit()
#     create_table(username, conn, cur)
#
# def create_table(username, conn, cur):
#     cur.execute("""CREATE TABLE {}(
#         routine_number INTEGER PRIMARY KEY ,
#         routine_name TEXT,
#         departure_time INTEGER,
#         start_location TEXT,
#         end_location TEXT
#         );""".format(username))
#     conn.commit()

def route_info():
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


def main():
    client = FacebookMessage.EchoBot("fortnite.killfeed@gmail.com", "fortnite")
    client.listen()

    # conn = sqlite3.connect("everything_db.sqlite")
    # cur = conn.cursor()
    #
    # cur.executescript("""CREATE TABLE IF NOT EXISTS Accounts(
    #         account_id INTEGER PRIMARY KEY,
    #         first_name TEXT,
    #         last_name TEXT,
    #         username TEXT,
    #         password TEXT
    #         );""")
    #
    # logged_in = False
    # while not logged_in:
    #     print("1. Login")
    #     print("2. Signup")
    #     print("Anything else to quit")
    #     user_input = int(input("\nChoice: "))
    #
    #     if user_input == 1:
    #         print("attempting to login...")
    #         if login(cur):
    #             logged_in = True
    #             print("logged in")
    #         else:
    #             print("unable to login")
    #     elif user_input == 2:
    #         create_account(conn, cur)
    #         print("account has been created")
    #     else:
    #         exit()
    #
    #
    # # set up routine here




if __name__ == "__main__":
    main()