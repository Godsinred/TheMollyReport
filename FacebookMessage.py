from fbchat import log, Client
from fbchat.models import *
import threading
import queue
import Database
import requests


# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    KEY = "AIzaSyB_R-OTY2BwfqtjqWQ3eBPRfoTb8WywqFU"
    URL = "https://maps.googleapis.com/maps/api/directions/json"
    # key:  str(thread_id)
    # value: list[queue]
    conversations = {}
    database = Database.Database(threading.Lock())

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        print("author_id: {}, thread_id: {}, thread_type: {}, UID: {}".format(author_id, thread_id, thread_type,
                                                                              self.uid))
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
            self.send_goodbye(thread_id, thread_type)
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
                    self.send(Message(text="you are now logged in"), thread_id=thread_id, thread_type=thread_type)
                else:
                    self.send(Message(text="unable to login"), thread_id=thread_id, thread_type=thread_type)

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

                self.database.create_account(first, last, username, password, int(thread_id), str(thread_type))
                self.send(Message(text="account has been created"), thread_id=thread_id, thread_type=thread_type)

            else:
                self.send_goodbye(thread_id, thread_type)
                self.conversations.pop(thread_id)
                return

            if not logged_in:
                self.send_main_menu(thread_id, thread_type)

                try:
                    user_input = int(self.conversations[thread_id].get())
                except:
                    self.send_goodbye(thread_id, thread_type)
                    self.conversations.pop(thread_id)
                    return

        self.route_main_page(thread_id, thread_type, username)

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
        msg = "--- Home ---\nPlease enter in the number of the choice below.\n1. Login\n2. Signup\nAnything else to quit\n\nNumber:"
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def send_route_menu(self, thread_id, thread_type):
        msg = "--- Routes ---\n1. View Routes\n2. Create Route\n3. Delete Route\n4. Update Route\nAnything else to quit and logout\n\nNumber of Choice:"
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def send_goodbye(self, thread_id, thread_type):
        self.send(Message(text="Thank you for using the Molly Report! Goodbye"), thread_id=thread_id,
                  thread_type=thread_type)

    def route_main_page(self, thread_id, thread_type, username):
        self.send_route_menu(thread_id, thread_type)

        try:
            user_input = int(self.conversations[thread_id].get())
        except:
            self.send_goodbye(thread_id, thread_type)
            self.conversations.pop(thread_id)
            return

        done = False
        while not done:
            if user_input == 1:
                self.view_routes(thread_id, thread_type, username)

            elif user_input == 2:
                self.create_route(thread_id, thread_type, username)

            elif user_input == 3:
                self.delete_route(thread_id, thread_type, username)
            elif user_input == 4:
                self.update_route(thread_id, thread_type, username)
            elif user_input ==5:
                self.update_account(thread_id, thread_type, username)
            else:
                done = True
                self.send_goodbye(thread_id, thread_type)
                self.conversations.pop(thread_id)
                return

            self.send_route_menu(thread_id, thread_type)

            try:
                user_input = int(self.conversations[thread_id].get())
            except:
                done = True
                self.send_goodbye(thread_id, thread_type)
                self.conversations.pop(thread_id)
                return

    def view_routes(self, thread_id, thread_type, username):
        # this shows the whoel database, need to prettify and make it more useful to the user
        self.send(Message(text="--- Viewing all your routes ---"), thread_id=thread_id, thread_type=thread_type)
        data = self.database.get_all_routes(username)
        if data == []:
            self.send(Message(text="You have no routes."), thread_id=thread_id, thread_type=thread_type)

        else:
            for route in data:
                print(route)
                msg = "Route Name: {}\nStart: {}\nEnd: {}\nDeparture Time: {}".format(route[1], route[3], route[4],
                                                                                      route[2])
                self.send(Message(text=msg.replace('+', '  ')), thread_id=thread_id, thread_type=thread_type)

    def create_route(self, thread_id, thread_type, username):
        self.send(Message(text="--- Create Route --- "), thread_id=thread_id, thread_type=thread_type)
        self.send(Message(text="Enter your route name: "), thread_id=thread_id, thread_type=thread_type)
        name = self.conversations[thread_id].get()

        self.send(Message(text="Enter in your starting location:"), thread_id=thread_id, thread_type=thread_type)
        self.send(Message(text="Enter in Address line (ex. 123 Main Street): "), thread_id=thread_id,
                  thread_type=thread_type)
        address_line = self.conversations[thread_id].get()

        self.send(Message(text="Enter in City (ex. Los Angelos): "), thread_id=thread_id, thread_type=thread_type)
        city = self.conversations[thread_id].get()

        self.send(Message(text="Enter in State abbreviation (ex. CA): "), thread_id=thread_id, thread_type=thread_type)
        state = self.conversations[thread_id].get()

        self.send(Message(text="Enter in zip code (ex. 90210): "), thread_id=thread_id, thread_type=thread_type)
        zip = self.conversations[thread_id].get()

        start = address_line + '+' + city + '+' + state + '+' + zip

        self.send(Message(text="Enter in your ending location:"), thread_id=thread_id, thread_type=thread_type)
        self.send(Message(text="Enter in Address line (ex. 123 Main Street): "), thread_id=thread_id,
                  thread_type=thread_type)
        address_line = self.conversations[thread_id].get()

        self.send(Message(text="Enter in City (ex. Los Angelos): "), thread_id=thread_id, thread_type=thread_type)
        city = self.conversations[thread_id].get()

        self.send(Message(text="Enter in State abbreviation (ex. CA): "), thread_id=thread_id, thread_type=thread_type)
        state = self.conversations[thread_id].get()

        self.send(Message(text="Enter in zip code (ex. 90210): "), thread_id=thread_id, thread_type=thread_type)
        zip = self.conversations[thread_id].get()

        end = address_line + '+' + city + '+' + state + '+' + zip

        self.send(
            Message(text="Enter departure time in military time in PST (ex. 4:30 PM => 1630 or 6:00 AM => 600): "),
            thread_id=thread_id, thread_type=thread_type)
        time = self.conversations[thread_id].get()

        self.database.create_route(start, end, time, name, username)
        self.send(Message(text="Your route has been created."), thread_id=thread_id, thread_type=thread_type)


    def delete_route(self, thread_id, thread_type, username):
        self.view_routes(thread_id, thread_type, username)
        self.send(Message(text="Enter the number for the route you want to delete: "), thread_id=thread_id,
                  thread_type=thread_type)
        route_number = int(self.conversations[thread_id].get())

        name = self.database.delete_route(username,  route_number)
        msg = "\'{}\' has successfully been deleted".format(name)
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def update_route(self, thread_id, thread_type, username):
        self.view_routes(thread_id, thread_type, username)
        self.send(Message(text="Enter the number for the route you want to update: "), thread_id=thread_id, thread_type=thread_type)
        route_number = int(self.conversations[thread_id].get())

        msg = "What would you like to update about your route?\n1. Route Name\n2. Departuret time\n3. Start Location\n4. End Location\n\nChoice: "
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)
        route_update = int(self.conversations[thread_id].get())

        msg = "Enter in the new data: "
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)
        route_info = self.conversations[thread_id].get()

        self.database.update_route(username, route_number, route_update, route_info)

        msg = "Your route has been updated."
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)

    def update_account(self, thread_id, thread_type, username):
        msg = "What would you like to update about your account?\n1. First Name\n2. Last Name\n3. Username\n4. Password\nAnything else to quit.\n\nChoice: "
        self.send(Message(text=msg), thread_id=thread_id, thread_type=thread_type)
        user_input = int(self.conversations[thread_id].get())

        if user_input == 1:
            pass
        elif user_input == 2:
            pass
        elif user_input == 3:
            pass
        elif user_input == 4:
            pass





    def send_route_info(self, time):
        routes, user_info_list = self.database.get_routes_with_time(time)
        for route in routes:
            query = {"key": self.KEY, "destination": route[4], "origin": route[3], "avoid": "tolls",
                     "departure_time": "now", "traffic_model": "best_guess"}
            r = requests.get(self.URL, params=query)
            info = r.json()

            # pp = pprint.PrettyPrinter(indent = 4)
            # pp.pprint(info)
            print("URL: " + r.url)

            if info["status"] == "OK":
                print("Distance: " + info["routes"][0]["legs"][0]["distance"]["text"])
                print("Duration in Traffic: " + info["routes"][0]["legs"][0]["duration_in_traffic"]["text"])
            else:
                print("status != OK")

            print()

            route_msg = ''
            leg_num = 1
            for step in info["routes"][0]["legs"][0]["steps"]:
                inst = step["html_instructions"]
                present = True
                while present:
                    start = inst.find('<')
                    if start >= 0:
                        end = inst.find('>')
                        inst = inst[:start].strip() + ' ' + inst[end + 1:].strip()
                        # print(inst)
                    else:
                        present = False
                        route_msg += str(leg_num) + ") " + inst + '\n'
                        leg_num += 1

            # msg = "Distance: " + info["routes"][0]["legs"][0]["distance"]["text"] + '\n' + "Duration in Traffic: " + \
            #       info["routes"][0]["legs"][0]["duration_in_traffic"]["text"] + '\n' + route

            name = ''
            thread_id = ''
            thread_type = ''
            for i in user_info_list:
                if route[5] == i[1]:
                    name = i[0]
                    thread_id = i[2]
                    thread_type = i[3]
                    break
            print(thread_id)
            print(thread_type)

            route_msg = "Hi " + name + '\n' + "\nYour \'" + route[1] + "\' route report for today is:\n\n" + \
                         "Distance: " + info["routes"][0]["legs"][0]["distance"]["text"] + '\n' + \
                         "Duration in Traffic: " + info["routes"][0]["legs"][0]["duration_in_traffic"]["text"] + \
                        "\n\nYour route instructinos is: \n" + route_msg + "\n\nOpen in Google Maps? Coming Soon"
            self.send(Message(text=route_msg), thread_id=thread_id, thread_type=ThreadType.USER)