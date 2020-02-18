from slackcli.messages import Message
from slackcli.user import User


class Conversation:
    """Class representing a conversation for specific date."""
    def __init__(self, convo, date_obj, file):
        self.convo_id = file[0].split('/')[0]
        self.date_obj = date_obj
        self.raw_data = convo
        self.set_participants()
        self.set_messages()
        self.sort_messages()

    def set_participants(self):
        """Set conversation participants instance attribute."""
        users = [convo['members'] for convo in self.date_obj.convo_type
                 if convo.get('name') == self.convo_id
                 or convo.get('id') == self.convo_id]
        setattr(self, 'participants', [User(self.date_obj.export.users_json, user_id=user) for user in users[0]])

    def set_messages(self):
        """Set messages instance attribute with list of Messages in Conversation. Also,
        set time attribute of message for sorting in conversation."""
        setattr(self, 'messages', [Message(msg, self) for msg in self.raw_data])
        setattr(self, 'time', f'{self.messages[0].time}, {self.messages[0].tz}')

    def sort_messages(self):
        """Sort and structure messages based on time & thread status."""
        self.messages.sort(key=lambda msg: msg.ts)
        resorted_msgs = []
        for msg in self.messages:
            if msg.thread_parent:
                resorted_msgs.append(msg)
                for sub_msg in self.messages:
                    if sub_msg.thread_ts == msg.ts and not sub_msg.thread_parent:
                        resorted_msgs.append(sub_msg)
            elif msg.thread_child:
                ids = [msg.sender_id for msg in self.messages
                       if msg.thread_parent]
                thread_id = msg.thread_id
                if not msg.thread_id:
                    for message in self.messages:
                        if message.thread_parent and message.ts == msg.thread_ts:
                            thread_id = message.sender_id
                            break
                if thread_id not in ids:
                    resorted_msgs.append(msg)
                else:
                    continue
            else:
                resorted_msgs.append(msg)

        self.messages = resorted_msgs








