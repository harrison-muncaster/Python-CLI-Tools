from functools import lru_cache


class User:
    """Class represnting a Slack user with users profile data."""
    def __init__(self, users, **kwargs):
        self.users = users
        self.kwargs = kwargs

    @property
    @lru_cache(maxsize=1)
    def profile_data(self):
        """Cached Property: Users profile data."""
        data = None
        for user in self.users:
            if user['id'] == self.kwargs.get('user_id') or user['name'] == self.kwargs.get('username'):
                data = user
                break

            try:
                if user['profile']['email'].lower() == self.kwargs.get('email'):
                    data = user
                    break
            except KeyError:
                pass

            try:
                if user['profile']['bot_id'] == self.kwargs.get('bot_id'):
                    data = user
                    break
            except KeyError:
                pass

        return data

    @property
    @lru_cache(maxsize=1)
    def status(self):
        """Cached Property: Users Slack status. Internal, External, App."""
        if self.profile_data:
            status = 'Internal User' if not self.profile_data['is_bot'] else 'App'
        elif self.kwargs.get('user_id') == 'USLACKBOT':
            status = 'App'
        else:
            status = 'External User'
        return status

    @property
    @lru_cache(maxsize=1)
    def email(self):
        """Cached Property: Users email."""
        try:
            email = self.profile_data['profile']['email'].lower()
        except (TypeError, KeyError):
            email = self.kwargs.get('email')
        return email

    @property
    @lru_cache(maxsize=1)
    def full_name(self):
        """Cached Property: Users full name."""
        if self.kwargs.get('user_id') == 'USLACKBOT':
            name = 'Slackbot'
        else:
            try:
                name = self.profile_data['profile']['real_name']
            except (TypeError, KeyError):
                name = self.kwargs.get('username')
        return name

    @property
    @lru_cache(maxsize=1)
    def user_id(self):
        """Cached Property: Users Slack ID."""
        try:
            id = self.profile_data['id']
        except (TypeError, KeyError):
            id = self.kwargs.get('user_id')
        return id

    @property
    @lru_cache(maxsize=1)
    def user_name(self):
        """Cached Property: Users Slack username."""
        if self.kwargs.get('user_id') == 'USLACKBOT':
            name = 'Slackbot'
        else:
            try:
                name = self.profile_data['name']
            except (TypeError, KeyError):
                name = self.kwargs.get('username')
        return name

    @property
    @lru_cache(maxsize=1)
    def bot_id(self):
        """Cached Property: Bot ID"""
        try:
            id = self.profile_data['profile']['bot_id']
        except (TypeError, KeyError):
            id = None
        return id