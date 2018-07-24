import FacebookMessage
import threading
import time
import sqlite3

DAY = 86400 # amount of seconds in a day

def routine_check(client):
    conn = sqlite3.connect("everything_db.sqlite", check_same_thread=False)
    cur = conn.cursor()
    thread_lock = threading.Lock()
    while True:
        info = ''
        try:
            thread_lock.acquire(True)
            data = time.localtime()
            current_time = data.tm_hour * 100 + data.tm_min
            cur.execute("SELECT time FROM Times WHERE time={}".format(current_time))
            info = cur.fetchone()
        finally:
            thread_lock.release()

        if info != None:
            client.send_route_info(current_time)
            time.sleep(30)

        time.sleep(30)

def main():
    client = FacebookMessage.EchoBot("fortnite.killfeed@gmail.com", "fortnite")
    t = threading.Thread(target=routine_check, args=(client,), daemon=True)
    t.start()
    client.listen()



if __name__ == "__main__":
    main()