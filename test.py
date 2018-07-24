from fbchat import log, Client
# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
            self.markAsDelivered(thread_id, message_object.uid)
            self.markAsRead(thread_id)
            print(type(thread_id))
            print(type(thread_type))
            log.info("{} from {} in {}".format(message_object, thread_id, thread_type. name))
            # If you're not the author, echo
            if author_id != self.uid:
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

client = EchoBot("fortnite.killfeed@gmail.com", "fortnite")
client.listen()