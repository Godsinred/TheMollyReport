import requests
import pprint
import sqlite3
import getpass
import sys
import FacebookMessage


KEY = "AIzaSyB_R-OTY2BwfqtjqWQ3eBPRfoTb8WywqFU"
DAY = 86400 # amount of seconds in a day
URL = "https://maps.googleapis.com/maps/api/directions/json"

def main():
    client = FacebookMessage.EchoBot("fortnite.killfeed@gmail.com", "fortnite")
    client.listen()



if __name__ == "__main__":
    main()