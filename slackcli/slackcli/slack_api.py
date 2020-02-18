import os
import click
from slack import WebClient
from slack.errors import SlackApiError


def token():
    try:
        token = f'{os.environ["SLACK_CLI_API"]}'
    except KeyError:
        raise click.ClickException(('Slack API token cannot be found.\n'
                                    'Please add the following line to your Bash Profile.\n'
                                    'export SLACK_CLI_API="{api token}"'))
    return token


class SlackAPI:
    """Class representing the Slack API."""
    def __init__(self, channel=None, user=None):
        self.slack = WebClient(token=token())
        self.channel = channel
        self.user = user

    def lookup_user_by_email(self):
        """Lookup user by email & parse relevant info."""
        try:
            r = self.slack.users_lookupByEmail(email=self.user)
        except SlackApiError as e:
            print(f'\r{70 * " "}', end='\r', flush=True)
            raise click.BadParameter(f'User {self.user} could not be found.')

        info = self.parse_user_info(r)
        return info

    def lookup_user_by_id(self):
        """Lookup user by ID & parse relevant info."""
        try:
            r = self.slack.users_profile_get(user=self.user)
        except SlackApiError as e:
            print(f'\r{70 * " "}', end='\r', flush=True)
            raise click.BadParameter(f'User {self.user} could not be found.')

        info = self.parse_user_info(r)
        return info

    def parse_user_info(self, data):
        """Parse & return dict of relevant user info."""
        if not data.get('user'):
            email = data['profile']['email']
            data = self.slack.users_lookupByEmail(email=email)

        info = {
            'Name': data['user']['real_name'],
            'ID': data['user']['id'],
            'Admin': data['user']['is_admin'],
            'Owner': data['user']['is_owner']
        }
        return info

    def lookup_channels(self):
        """Lookup & parse relevant channel."""
        r = self.slack.conversations_list(types='public_channel, private_channel',
                                          limit=1000, exclude_archived='true')
        while True:
            rel_chan = self.parse_relevant_channel(r['channels'])
            next_cursor = (r['response_metadata']['next_cursor']
                           if r['response_metadata'].get('next_cursor')
                           else False)

            if not next_cursor or rel_chan:
                break
            try:
                r = self.slack.conversations_list(cursor=next_cursor,
                                                  limit=1000, types='public_channel, private_channel',
                                                  exclude_archived='true')

            except SlackApiError as e:
                print(e.args)

        return rel_chan

    def parse_relevant_channel(self, channels):
        """Parse relevant channel ID from list of channels."""
        data = None
        for chan in channels:
            if chan['name'] == self.channel:
                data = chan['id']
                break
        return data

    def channel_data(self):
        """Lookup relevant channel and return channel data."""
        try:
            data = self.slack.conversations_info(channel=self.channel)
            if 'error' in data:
                raise Exception

        except Exception:
            id = self.lookup_channels()
            if not id:
                print(f'\r{70 * " "}', end='\r', flush=True)
                raise click.BadParameter(f'Channel {self.channel} could not be located.')
            data = self.slack.conversations_info(channel=id)
        return data

    def parse_channel_members(self, data):
        """Parse return all members/member data (list) of relevant channel."""
        id = data['channel']['id']
        r = self.slack.conversations_members(channel=id, limit=1000)
        members = r['members']
        while True:
            next_cursor = (r['response_metadata']['next_cursor']
                           if r['response_metadata'].get('next_cursor')
                           else False)
            if not next_cursor:
                break
            r = self.slack.conversations_members(channel=id, limit=1000, cursor=next_cursor)
            members += r['members']
        members_list = []
        for member in members:
            r = self.slack.users_profile_get(user=member)
            members_list.append((r['profile']['real_name'], r['profile']['email'] if r['profile'].get('email') else None))

        return members_list

    @staticmethod
    def parse_channel_info(data):
        """Parse relevant channel info."""
        chan_info = {
            'Name': data['channel']['name'],
            'ID': data['channel']['id'],
            'Type': 'Private' if data['channel']['is_private'] else 'Public'
        }
        return chan_info

    def complete_channel_info(self):
        """Collect & return relevant complete channel info."""
        data = self.channel_data()
        chan_info = self.parse_channel_info(data)
        members = self.parse_channel_members(data)
        chan_info['# of Members'] = len(members)
        return {'info': chan_info,
                'members': members}
