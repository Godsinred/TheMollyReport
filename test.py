import time
import sqlite3
import threading
conn = sqlite3.connect("everything_db.sqlite", check_same_thread=False)
cur = conn.cursor()
thread_lock = threading.Lock()
info = ''
try:
    thread_lock.acquire(True)
    data = time.localtime()
    current_time = 2326
    cur.execute("SELECT time FROM Times WHERE time={}".format(current_time))
    info = cur.fetchone()
    cur.execute("SELECT * from Times")
    data = cur.fetchall()
    print(data)
finally:
    thread_lock.release()

if info != None:
    print("it got something")
