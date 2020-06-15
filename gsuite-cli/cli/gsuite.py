
import requests
import os
import hashlib
from urllib.parse import urlencode
from functools import cached_property

import pickle
from password_generator import PasswordGenerator
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GSuite:
    """Class that represents a GSuite object."""
    def __init__(self, args):
        """Initialize instance of GSuite class."""
        self.arg = args.values
        self.scopes = ['https://www.googleapis.com/auth/admin.directory.user',
                       'https://www.googleapis.com/auth/admin.directory.group.member',
                       'https://www.googleapis.com/auth/admin.directory.user.security']
        self.client = build('admin', 'directory_v1', credentials=self.credentials)

    @cached_property
    def credentials(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('../files/token.pickle'):
            with open('../files/token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../files/credentials.json', self.scopes)
                creds = flow.run_console()

            # Save the credentials for the next run
            with open('../files/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    @cached_property
    def verification_codes(self):
        """Return LIST of first 3 verification codes for a specific GSuite user."""
        try:
            data = self.client.verificationCodes().list(userKey=self.arg.email).execute()['items']
        except errors.HttpError as e:
            raise SystemExit(e)
        codes = [code['verificationCode'] for code in data]
        return f'{codes[0]}, {codes[1]}, {codes[2]}'

    @cached_property
    def users(self):
        """Cached Property: Return SET of all GSuite users emails."""
        try:
            data = self.client.users().list(customer='my_customer', orderBy='email', maxResults=500).execute()['users']
        except errors.HttpError as e:
            raise SystemExit(e)
        users = {user['primaryEmail'] for user in data if not user['suspended']}
        return users

    def user_info(self, email):
        """Return DICT(first name, last name, email, status) of a single GSuite user."""
        try:
            data = self.client.users().get(userKey=email).execute()
        except errors.HttpError as e:
            raise SystemExit(e)
        return data

    def create_user(self):
        """Create new user in GSuite & return JSON response."""
        payload = {
            'primaryEmail': self.arg.email,
            'name': {
                'givenName': self.arg.email.split('@')[0].split('.')[0].capitalize(),
                'familyName': self.arg.email.split('@')[0].split('.')[1].capitalize()
            },
            'password': self.hash_pwd(),
            'hashFunction': 'SHA-1'
        }
        try:
            data = self.client.users().insert(body=payload).execute()
        except errors.HttpError as e:
            raise SystemExit(e)
        return data

    def add_user_to_group(self, group):
        """Add user to GSuite group and return JSON response."""
        payload = {
            'email': self.arg.email,
            'role': 'MEMBER'
        }
        try:
            data = self.client.members().insert(groupKey=group, body=payload).execute()
        except errors.HttpError as e:
            raise SystemExit(e)
        return data

    def generate_verification_codes(self):
        """Generate new GSuite user verification codes and return response."""
        try:
            data = self.client.verificationCodes().generate(userKey=self.arg.email).execute()
        except errors.HttpError as e:
            raise SystemExit(e)
        return data

    def generate_flashpaper_link(self):
        """Generate & return a flashpaper link."""
        url = f"{FLASHPAPER_URL}/add"
        payload_dict = {'secret': f'Password: {self.password}\nVerification Codes: {self.verification_codes}'}
        payload = urlencode(payload_dict)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, headers=headers, data=payload)

        for line in response.text.split('\n'):
            if FLASHPAPER_URL in line:
                link = line.split('</h4>')[0].split('>')[1]

        return link

    def hash_pwd(self):
        """Create & return a SHA-1 hash of the users password."""
        sha1 = hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        return sha1.hexdigest()

    @cached_property
    def password(self):
        """Create & return a 16-30 char alphanumeric password."""
        pwo = PasswordGenerator()
        pwo.minlen = 16
        pwo.maxlen = 30
        pwo.minuchars = 1
        pwo.minlchars = 1
        pwo.minnumbers = 1
        pwo.minschars = 1
        return pwo.generate()
