# import sqlite3
#
# conn = sqlite3.connect("everything_db.sqlite")
# cur = conn.cursor()
#
# username = "Test"
# password = "Admin"
# cmd = """SELECT account_id FROM Accounts WHERE username = \'?\' AND password = \'?\'"""
# params = (username, password)
# try:
#
#
#     cur.execute(cmd)
#     data = cur.fetchone()
# finally:
#     pass
#
# if data != None:
#     print("found")
# else:
#     print("not found")

import time

print("time.localtime(): " + str(time.localtime()))
print("time.clock(): " + str(time.clock()))
print("time.get_clock_info(clock): " + str(time.get_clock_info("clock")))
print("time.get_clock_info(time): " + str(time.get_clock_info("time")))
