import requests
import json
import os
from functools import cached_property


class FreshService:
    """Class that represents a FreshService API object."""
    def __init__(self):
        """Initialize an instance of FreshService class."""
        self.url = 'https://disqo.freshservice.com/api/v2'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {os.environ["FRESH_API"]}'
        }

    def get(self, endpoint, params=None):
        """Return response of GET Request."""
        try:
            r = requests.get(f'{self.url}/{endpoint}', headers=self.headers, params=params)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(f'FreshService {e}')
        data = r.json()
        while r.headers.get('link'):
            r, data = self.get_page(r, data)
        return data

    def get_page(self, r, data):
        """Return PAGINATED response of GET Request."""
        next_page = r.headers['link'].split('<')[1].split('>')[0]
        r = requests.get(next_page, headers=self.headers)
        r_json = r.json()
        key = list(r_json.keys())[0]
        for item in r_json[key]:
            data[key].append(item)
        return r, data

    def post(self, endpoint, payload=None):
        """Return response of POST Request."""
        r = requests.post(f'{self.url}/{endpoint}', headers=self.headers, data=payload)
        return r.json()

    def delete(self, endpoint):
        """Return response of DELETE Request."""
        r = requests.delete(f'{self.url}/{endpoint}', headers=self.headers)
        return r

    @cached_property
    def users(self):
        """Cached Property: Return SET of all FreshService user emails."""
        data = self.get(f'requesters', {'per_page': 100})['requesters']
        requesters = {user['primary_email'] for user in data if user['active']}
        return requesters

    @cached_property
    def agents(self):
        """Cached Property: Return SET of all FreshService agent emails."""
        data = self.get(f'agents', {'per_page': 20})['agents']
        agents = {agent['email'] for agent in data if agent['active']}
        return agents

    def create_user(self, **kwargs):
        """Return response from CREATE USER POST Request to FreshService."""
        user_profile = {
            'first_name': kwargs['first_name'],
            'last_name': kwargs['last_name'],
            'primary_email': kwargs['email']
        }
        data = self.post('requesters', payload=json.dumps(user_profile))
        return data

    def delete_user(self, user_id):
        """Return response from DELETE USER Request to FreshService."""
        data = self.delete(f'requesters/{user_id}')
        return data

    def lookup_user_by_email(self, user_email):
        """Return response(dict) from LOOKUP USER Request to FreshService."""
        data = self.get(f'requesters', {'per_page': 100})['requesters']
        user = (next(user for user in data if user['primary_email'] == user_email))
        return user
