from fbchat import log, Client
from fbmessenger import quick_replies
from fbchat.models import *
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
                quick_reply_1 = quick_replies.QuickReply(title='Location', content_type='location')
                quick_replies_set = quick_replies.QuickReplies(quick_replies=[
                    quick_reply_1
                ])
                text = {'text': 'Share your location'}
                text['quick_replies'] = quick_replies_set.to_dict()
                quick_replies = [
                    QuickReply(title="Action", payload="PICK_ACTION"),
                    QuickReply(title="Comedy", payload="PICK_COMEDY")
                ]
                self.send(Message(text=text), thread_id=thread_id, thread_type=thread_type)

client = EchoBot("TheOfficialMollyReport@gmail.com", "themolly")
client.listen()