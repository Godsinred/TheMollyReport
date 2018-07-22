from fbchat import log, Client
from fbchat.models import *
import threading
import time
import queue
import Database

# Subclass fbchat.Client and override required methods
class EchoBot(Client):

    # key:  int(thread_id)
    # value: list[queue]
    conversations = {}
    database = Database.Database(threading.Lock())
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        print("author_id: {}, thread_id: {}, thread_type: {}, UID: {}".format(author_id, thread_id, thread_type, self.uid))
        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        print(message_object.text)
        # If you're not the author, echo
        if author_id != self.uid:
            self.check_open_conversation(thread_id, thread_type, message_object)
        # self.send(message_object, thread_id=thread_id, thread_type=thread_type)

    def check_open_conversation(self, thread_id, thread_type, message_object):
        if thread_id not in self.conversations:
            q = queue.Queue()
            self.conversations[thread_id] = q
            t = threading.Thread(target=self.start_conversation, args=(thread_id, thread_type), daemon=True)
            t.start()

        else:
            self.conversations[thread_id].put(message_object.text)

    def start_conversation(self, thread_id, thread_type):
        self.send(Message(text="Hello Welcome to The Molly Report"), thread_id=thread_id, thread_type=thread_type)
        self.send_main_menu(thread_id, thread_type)

        try:
            user_input = int(self.conversations[thread_id].get())
        except:
            self.conversations.pop(thread_id)
            return

        logged_in = False
        while not logged_in:
            if user_input == 1:
                msg = "attempting to login..."
                self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

                self.send(Message(text="Enter your username: "), thread_id=thread_id, thread_type=thread_type)
                username = self.conversations[thread_id].get()

                self.send(Message(text="Enter your password: "), thread_id=thread_id, thread_type=thread_type)
                password = self.conversations[thread_id].get()

                if self.database.login(username, password):
                    logged_in = True
                    self.send(Message(text="logged in"), thread_id=thread_id, thread_type=thread_type)
                else:
                    print("unable to login")
            elif user_input == 2:
                self.send(Message(text="Enter in first name: "), thread_id=thread_id, thread_type=thread_type)
                first = self.conversations[thread_id].get()

                self.send(Message(text="Enter in last name: "), thread_id=thread_id, thread_type=thread_type)
                last = self.conversations[thread_id].get()

                self.send(Message(text="Enter in username: "), thread_id=thread_id, thread_type=thread_type)
                username = self.conversations[thread_id].get()

                self.send(Message(text="Enter in password: "), thread_id=thread_id, thread_type=thread_type)
                password = self.conversations[thread_id].get()

                username = self.check_username(username, thread_id, thread_type)

                self.database.create_account(first, last, username, password)
                self.send(Message(text="account has been created"), thread_id=thread_id, thread_type=thread_type)

            else:
                self.conversations.pop(thread_id)
                break;

            if not logged_in:
                self.send_main_menu(thread_id, thread_type)

                try:
                    user_input = int(self.conversations[thread_id].get())
                except:
                    return
        


    def check_username(self, username, thread_id, thread_type):
        self.database.cur.execute("SELECT username FROM Accounts")
        all_usernames = self.database.cur.fetchall()
        clean_all_user = []
        for user in all_usernames:
            clean_all_user.append(user[0])
        while username in clean_all_user:
            self.send(Message(text="Username: \"{}\" is already taken. Please choose a new username.".format(username)),
                    thread_id=thread_id, thread_type=thread_type)
            self.send(Message(text="Enter in new username: "), thread_id=thread_id, thread_type=thread_type)
            username = self.conversations[thread_id].get()

        return username

    def send_main_menu(self, thread_id, thread_type):
        msg = "Please choose an option below.\n1. Login\n2. Signup\nAnything else to quit\nChoice:"
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)
