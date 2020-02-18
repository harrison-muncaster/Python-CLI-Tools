from datetime import datetime, timezone
from functools import lru_cache
from slackcli.user import User



class Message:
    """Class representing a message in a specific conversation."""
    def __init__(self, msg, convo_obj):
        self.raw_data = msg
        self.convo_obj = convo_obj
        self.append_user_to_convo()

    def append_user_to_convo(self):
        """Append user to convo participants if not already present."""
        for user in self.convo_obj.participants:
            if (user.user_id == self.sender_id and not user.full_name
                    or user.user_id != self.sender_id and user.user_name == self.sender_user_name
                    or self.sender_id and self.sender_id == user.bot_id and self.sender_id != user.user_id):
                self.convo_obj.participants.remove(user)
                break
        bot_ids = [user.bot_id for user in self.convo_obj.participants]
        user_ids = [user.user_id for user in self.convo_obj.participants]
        users = [*bot_ids, *user_ids]
        if self.sender_id not in users:
            user = User(self.convo_obj.date_obj.export.users_json,
                        user_id=self.sender_id,
                        username=self.sender_full_name)
            self.convo_obj.participants.append(user)

    @property
    @lru_cache(maxsize=1)
    def sender_id(self):
        """Cached Property: Sender ID."""
        id = None
        for user in self.convo_obj.participants:
            if self.sender_user_name and self.sender_user_name == user.user_name:
                id = user.user_id
                break
        if not id:
            if self.raw_data.get('user') or self.raw_data.get('bot_id'):
                try:
                    id = self.raw_data['user']
                except KeyError:
                    id = self.raw_data['bot_id']

            else:
                try:
                    id = self.raw_data['original']['user']
                except KeyError:
                    try:
                        id = self.raw_data['original']['bot_id']
                    except KeyError:
                        try:
                            id = self.raw_data['message']['user']
                        except KeyError:
                            try:
                                id = self.raw_data['message']['bot_id']
                            except KeyError:
                                id = None
        return id

    @property
    @lru_cache(maxsize=1)
    def sender_full_name(self):
        """Cached Property: Sender full name."""
        name = None
        for user in self.convo_obj.participants:
            if self.sender_id == user.user_id and user.full_name:
                name = user.full_name
                break
        if not name:
            try:
                name = self.raw_data['user_profile']['real_name']
            except KeyError:
                try:
                    name = self.raw_data['original']['user_profile']['real_name']
                except KeyError:
                    try:
                        name = self.raw_data['username']
                        for user in self.convo_obj.participants:
                            if user.user_name == name:
                                name = user.full_name
                    except KeyError:
                        try:
                            name = self.raw_data['original']['username']
                            for user in self.convo_obj.participants:
                                if user.user_name == name:
                                    name = user.full_name
                        except KeyError:
                            name = None
        return name

    @property
    @lru_cache(maxsize=1)
    def sender_user_name(self):
        """Cached Property: Sender username."""
        try:
            name = self.raw_data['user_profile']['name']
        except KeyError:
            try:
                name = self.raw_data['username']
            except KeyError:
                try:
                    name = self.raw_data['original']['username']
                except KeyError:
                    try:
                        name = self.raw_data['message']['username']
                    except KeyError:
                        name = None
        return name

    @property
    @lru_cache(maxsize=1)
    def sender_email(self):
        """Cached Property: Sender email."""
        email = None
        for user in self.convo_obj.participants:
            if user.user_id == self.sender_id:
                email = user.email
                break
        return email

    @property
    @lru_cache(maxsize=1)
    def sender_status(self):
        """Cached Property: Sender Slack status."""
        status = None
        for user in self.convo_obj.participants:
            if (self.sender_id == user.user_id
                    or self.sender_full_name == user.full_name
                    or self.sender_user_name == user.user_name):
                status = user.status
                break
        return status

    @property
    @lru_cache(maxsize=1)
    def text(self):
        """Cached Property: Message text body."""
        try:
            try:
                text = self.raw_data['text']
                if text == '':
                    text = '[NO TEXT]'
            except KeyError:
                try:
                    text = self.raw_data['original']['text']
                except KeyError:
                    try:
                        text = self.raw_data['message']['text']
                    except KeyError:
                        raise
        except KeyError:
            text = '[NO TEXT]'

        if self.raw_data.get('files') or self.raw_data.get('original', {}).get('files'):
            text = self.parse_msg_files(text)

        if self.raw_data.get('attachments'):
            text = self.parse_msg_attachments(text)

        text = self.format_user_mentions(text)
        if self.raw_data.get('reactions') and self.convo_obj.date_obj.export.input_email:
            text = self.reactions_added(text)

        return text

    def parse_msg_files(self, text):
        """Parse message files if present & append to message text body."""
        try:
            try:
                file = self.raw_data['files'][0]['name']
            except KeyError:
                try:
                    file = self.raw_data['files'][0]['title']
                except KeyError:
                    try:
                        file = self.raw_data['files'][0]['id']
                    except KeyError:
                        try:
                            file = self.raw_data['original']['files'][0]['name']
                        except KeyError:
                            try:
                                file = self.raw_data['message']['files'][0]['name']
                            except KeyError:
                                raise

        except KeyError:
            updated_text = f"{text}<br/> » [FILE ATTACHED]"
        else:
            updated_text = f"{text}<br/> » [FILE ATTACHED]-[{file}]"

        try:
            id = self.raw_data['files'][0]['user']
            user = User(self.convo_obj.date_obj.export.users_json, user_id=id)
            updated_text = f"{text}<br/> » [FILE ATTACHED]-[{file}]-[File originally posted by @{user.full_name}]"
        except KeyError:
            pass

        return updated_text

    def parse_msg_attachments(self, text):
        """Parse message attachments if present & append to message text body."""
        try:
            try:
                file = self.raw_data['attachments'][0]['fallback']
            except KeyError:
                try:
                    file = self.raw_data['attachments'][0]['image_url']
                except KeyError:
                    raise
        except KeyError:
            updated_text = f"{text}<br/> » [FILE ATTACHED]"
        else:
            updated_text = f"{text}<br/> » [FILE ATTACHED]-[{file}]"

        return updated_text

    @property
    @lru_cache(maxsize=1)
    def ts(self):
        """Cached Property: Message timestamp."""
        if not self.edited_ts and not self.original_ts:
            if not self.thread:
                try:
                    ts = self.raw_data['ts']
                except KeyError:
                    pass
            else:
                try:
                    if self.raw_data.get('message'):
                        ts = self.raw_data['message']['ts']
                    else:
                        ts = self.raw_data['ts']
                except KeyError:
                    pass
        elif self.original:
            ts = self.original_ts
        elif self.edited:
            ts = self.edited_ts
        return ts

    @property
    @lru_cache(maxsize=1)
    def date_time_obj(self):
        """Cached Property: Date/time object from message."""
        ts = float(self.ts)
        date_time_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
        return date_time_utc

    @property
    @lru_cache(maxsize=1)
    def date(self):
        """Cached Property: Formatted date."""
        date = self.date_time_obj.astimezone().strftime('%Y-%m-%d')
        return date

    @property
    @lru_cache(maxsize=1)
    def time(self):
        """Cached Property: Formatted time."""
        time = self.date_time_obj.astimezone().strftime('%H:%M:%S')
        return time

    @property
    @lru_cache(maxsize=1)
    def tz(self):
        """Cached Property: Timezone."""
        tz = self.date_time_obj.astimezone().tzinfo
        return tz

    @property
    @lru_cache(maxsize=1)
    def thread(self):
        """Cached Property: Thread status."""
        status = (True if self.raw_data.get('reply_count')
                  else True if self.raw_data.get('thread_ts')
                  else True if self.raw_data.get('message', {}).get('thread_ts')
                  else False)
        return status

    @property
    @lru_cache(maxsize=1)
    def thread_ts(self):
        """Cached Property: Thread timestamp."""
        try:
            ts = self.raw_data['thread_ts']
        except KeyError:
            try:
                ts = self.raw_data['message']['thread_ts']
            except KeyError:
                ts = None
        return ts

    @property
    @lru_cache(maxsize=1)
    def thread_parent(self):
        """Cached Property: Thread parent status."""
        return True if self.ts == self.thread_ts else False

    @property
    @lru_cache(maxsize=1)
    def thread_child(self):
        """Cached Property: Thread child status."""
        return True if self.thread and self.ts != self.thread_ts else False

    @property
    @lru_cache(maxsize=1)
    def thread_id(self):
        """Cached Property: Thread ID."""
        if self.thread_child:
            try:
                id = self.raw_data['parent_user_id']
            except KeyError:
                try:
                    id = self.raw_data['message']['parent_user_id']
                except KeyError:
                    try:
                        id = self.raw_data['original']['parent_user_id']
                    except KeyError:
                        try:
                            id = self.raw_data['root']['user']
                        except KeyError:
                            id = None
        else:
            id = None
        return id

    @property
    @lru_cache(maxsize=1)
    def original(self):
        """Cached Property: Original status."""
        return True if self.raw_data.get('original') else False

    @property
    @lru_cache(maxsize=1)
    def original_ts(self):
        """Cached Property: Original timestamp."""
        try:
            ts = self.raw_data['original']['ts']
        except KeyError:
            ts = None
        return ts

    @property
    @lru_cache(maxsize=1)
    def edited(self):
        """Cached Property: Edited status."""
        status = (True if self.raw_data.get('edited')
                  else True if self.raw_data.get('message', {}).get('edited')
                  else False)
        return status

    @property
    @lru_cache(maxsize=1)
    def edited_ts(self):
        """Cached Property: Edited timestamp."""
        try:
            ts = self.raw_data['edited']['ts']
        except KeyError:
            try:
                ts = self.raw_data['message']['edited']['ts']
            except KeyError:
                ts = None
        return ts

    @property
    @lru_cache(maxsize=1)
    def edited_by(self):
        """Cached Property: Edited by."""
        try:
            user = self.raw_data['edited']['user']
        except KeyError:
            try:
                user = self.raw_data['edited_by']
            except KeyError:
                user = None
        return user

    @property
    @lru_cache(maxsize=1)
    def deleted(self):
        """Cached Property: Deleted status."""
        return True if self.raw_data.get('deleted_by') else True if self.raw_data.get('deleted_ts') else None

    @property
    @lru_cache(maxsize=1)
    def deleted_ts(self):
        """Cached Property: Deleted timestamp."""
        try:
            ts = self.raw_data['deleted_ts']
        except KeyError:
            ts = None
        return ts

    @property
    @lru_cache(maxsize=1)
    def deleted_by(self):
        """Cached Property: Deleted by."""
        try:
            user = self.raw_data['deleted_by']
        except KeyError:
            user = None
        return user

    def reactions_added(self, text):
        """Format reactions added by specified user and append to message text body."""
        updated_text = text
        user = self.convo_obj.date_obj.export.target_user
        users = [id for reaction in self.raw_data['reactions']
                 for id in reaction['users']
                 if id == user.user_id]
        if user.user_id in users:
            updated_text = f"{text}<br/> » [Emoji Reaction added by @{user.full_name}]"
        return updated_text

    def format_user_mentions(self, text):
        """Format user, group, and email mentions."""
        words = text.split()
        for index, word in enumerate(words):
            if word.startswith('<@'):
                parsed_id = word.split('@')[1].split('>')[0]
                user = User(self.convo_obj.date_obj.export.users_json, user_id=parsed_id)
                if user.full_name:
                    words[index] = f'@{user.full_name}'
                else:
                    continue
            elif word.startswith('<http'):
                parsed_word = word.split('<')[1].split('>')[0]
                words[index] = parsed_word
            elif word.startswith('<mailto:'):
                parsed_word = word.split('|')[1].split('>')[0]
                words[index] = parsed_word
            elif word.startswith('<!subteam'):
                parsed_word = word.split('|')[1].split('>')[0]
                words[index] = parsed_word
            elif word.startswith('<!'):
                parsed_word = f"@{word.split('!')[1].split('>')[0]}"
                words[index] = parsed_word
        new_str = ' '
        text = new_str.join(words)
        return text



