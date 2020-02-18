import json
import re
import os
from datetime import datetime
from functools import lru_cache

import click
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


from slackcli.user import User
from slackcli.dates import Date


class Export:
    """Export Class: Handles bulk of ZIP file validation and convo object creation."""
    def __init__(self, email=None, dates=None, channel=None):
        self.target_user = None
        self.input_email = email
        self.input_date_range = dates
        self.input_channel = channel
        self.zip_file = None


    @property
    def zip_file(self):
        """Getter Property: zip_file."""
        return self._zip_file

    @zip_file.setter
    def zip_file(self, file):
        """Setter Property: zip_file."""
        self._zip_file = file

    @property
    @lru_cache(maxsize=1)
    def users_json(self):
        """Cached Property: users json file."""
        return self.open_json_file('users.json')

    @property
    @lru_cache(maxsize=1)
    def dms_json(self):
        """Cached Property: dms json file."""
        return self.open_json_file('dms.json')

    @property
    @lru_cache(maxsize=1)
    def mpims_json(self):
        """Cached Property: mpims json file."""
        return self.open_json_file('mpims.json')

    @property
    @lru_cache(maxsize=1)
    def groups_json(self):
        """Cached Property: groups json file."""
        return self.open_json_file('groups.json')

    @property
    @lru_cache(maxsize=1)
    def channels_json(self):
        """Cached Property: channels json file."""
        return self.open_json_file('channels.json')

    @property
    @lru_cache(maxsize=1)
    def dms_files(self):
        """Cached Property: relevant dms files."""
        return self.parse_dms_mpims_files(self.dms_json)

    @property
    @lru_cache(maxsize=1)
    def mpims_files(self):
        """Cached Property: relevant mpims files."""
        return self.parse_dms_mpims_files(self.mpims_json)

    @property
    @lru_cache(maxsize=1)
    def channels_files(self):
        """Cached Property: relevant channel files."""
        return self.parse_group_channel_files(self.channels_json)

    @property
    @lru_cache(maxsize=1)
    def groups_files(self):
        """Cached Property: relevant group files."""
        return self.parse_group_channel_files(self.groups_json)

    @property
    @lru_cache(maxsize=1)
    def file_list(self):
        """Cached Property: all json files in zip_file or all json files of specified channel."""
        if not self.input_channel:
            files = sorted((file, file.split('/')[1].split('.')[0]) for file in self.zip_file.namelist()
                           if '/' in file and file.endswith('.json'))
        else:
            files = sorted((file, file.split('/')[1].split('.')[0]) for file in self.zip_file.namelist()
                           if file.startswith(f'{self.input_channel}/') and file.endswith('.json'))
        return files

    @property
    @lru_cache(maxsize=1)
    def available_dates(self):
        """Cached Property: All available dates in file_list property."""
        dates = sorted({file[1] for file in self.file_list})
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        return dates

    @property
    @lru_cache(maxsize=1)
    def relevant_dates(self):
        """Cached Property: All relevant dates within specified date range."""
        try:
            dates = [date for date in self.available_dates
                     if self.input_date_range[0] <= date <= self.input_date_range[-1]]
        except IndexError:
            dates = self.available_dates
        return dates

    @staticmethod
    def parse_dates_from_files(files):
        """Parse & sort dates from file names."""
        dates = sorted({date[1] for date in files})
        return dates

    def open_json_file(self, file):
        """Open JSON file."""
        with self.zip_file.open(file) as json_file:
            data = json_file.read()
            return json.loads(data)

    def parse_group_channel_files(self, json_file):
        """Parse relevant Group & Channel files."""
        channels = [channel['name'] for channel in json_file]
        files = self.file_list
        if self.input_email:
            files = [file for file in files
                     if file[0].split('/')[0] in channels
                     and re.search(self.target_user.user_id, json.dumps(self.open_json_file(file[0])))]
            if not files:
                print(f'\r{70 * " "}', end='\r', flush=True)
                raise click.BadParameter(f'User {self.input_email} was not active in channel {self.input_channel}.')
        else:
            files = [file for file in self.file_list
                     if file[0].split('/')[0] in channels]
        if self.input_date_range:
            files = self.parse_date_relevant_files(files)
        return files

    def parse_dms_mpims_files(self, json_file):
        """Parse relevant DMS & MPIMS files."""
        ids = [dm['name'] if dm.get('name') else dm['id'] for dm in json_file
               if self.target_user.user_id in dm['members']]
        files = [file for file in self.file_list
                 if file[0].split('/')[0] in ids]
        if not files:
            print(f'\r{70 * " "}', end='\r', flush=True)
            raise click.BadParameter(f'User {self.input_email} was not active in any dms/mpdms.')

        if self.input_date_range:
            files = self.parse_date_relevant_files(files)
        return files

    def parse_date_relevant_files(self, files):
        """Parse date relevant files & return as list."""
        files = [file for file in files
                 if datetime.strptime(file[1], '%Y-%m-%d') in self.relevant_dates]
        return files

    def validate_input(self):
        """Validate input for user, channel, and dates options."""
        if self.input_email:
            if not re.search(self.input_email, json.dumps(self.users_json)):
                print(f'\r{70 * " "}', end='\r', flush=True)
                raise click.BadParameter(f'Could not locate {self.input_email} in users file.')
            id = next((user['id'] for user in self.users_json
                       if user['profile'].get('email', '').lower() == self.input_email))
            self.target_user = User(self.users_json, user_id=id, email=self.input_email)

        if self.input_channel:
            if (not re.search(self.input_channel, json.dumps(self.channels_json))
                    and not re.search(self.input_channel, json.dumps(self.groups_json))):
                print(f'\r{70 * " "}', end='\r', flush=True)
                raise click.BadParameter(f'Could not locate {self.input_channel} in channels file.')

        if self.input_date_range:
            for date in self.input_date_range:
                if self.available_dates[0] <= date <= self.available_dates[-1]:
                    continue
                else:
                    print(f'\r{70 * " "}', end='\r', flush=True)
                    raise click.BadParameter((f'Inputted date range is not within Export date range of '
                                              f'{self.available_dates[0].date()}-{self.available_dates[-1].date()}'))

    def create_convo_objects(self, files_list):
        """Create objects for all convos. Object structure: Date > Convo > Message.
        Set instance attributes to OBJs based off of convo-type. ie. dms, mpims, group, channel.
        """
        for file in files_list:
            files = getattr(self, f'{file}_files')
            if not files:
                continue
            dates = self.parse_dates_from_files(files)
            objects = [Date(self, files, date, getattr(self, f'{file}_json')) for date in dates]
            setattr(self, file, objects)


class Pdf(Export):
    """PDF Class. Handles creation of PDFs."""
    def __init__(self, email=None, date=None, channel=None):
        super().__init__(email, date, channel)
        self.date_heading_style = ParagraphStyle('heading', fontSize=18, leading=16, fontName='Helvetica-Bold')
        self.msg_heading_style = ParagraphStyle('msg_heading', fontSize=11, leading=14, fontName='Helvetica-Bold')
        self.msg_info_style = ParagraphStyle('msg_title', fontSize=9, leading=10, fontName='Helvetica-BoldOblique')
        self.msg_body_style = ParagraphStyle('msg_body', fontSize=9, leading=10, fontName='Helvetica')

    @staticmethod
    def create_blank_pdf(convo):
        """Create a blank PDF file."""
        pdf = SimpleDocTemplate(f'{convo}.pdf')
        return pdf

    @staticmethod
    def date_heading(convo_type, date):
        """Create PDF page heading based on convo-type."""
        title = {
            'dms': 'Direct Message Conversations',
            'mpims': 'Multi-Party Direct Message Conversations',
            'channels': 'Public Channel Conversations',
            'groups': 'Private Channel Conversations'
        }
        return f"<br/>{date} - {title[convo_type]}<br/><br/><br/>"

    @staticmethod
    def msg_heading(convo, convo_type):
        """Create message heading based on convo-type.
        Heading is channel name or convo participants with start time of convo.
        """
        if convo_type == 'dms' or convo_type == 'mpims':
            msg = [user.full_name for user in convo.participants]
        else:
            msg = convo.convo_id
        msg_heading = f'{msg} @ {convo.time}'
        return msg_heading

    @staticmethod
    def msg_info(msg):
        """Create message info for each message.
        Info is sender name, email/username, user status, message time, and timezone.
        """
        msg_info = (f'{msg.sender_full_name}, '
                f'{msg.sender_email if msg.sender_email else msg.sender_user_name}, '
                f'{msg.sender_status}, '
                f'{msg.time}, {msg.tz}')
        if msg.edited:
            msg_info = f'[EDITED] {msg_info}'
        if msg.deleted:
            msg_info = f'[DELETED] {msg_info}'
        if msg.original:
            msg_info = f'[ORIGINAL] {msg_info}'
        if msg.thread_child:
            msg_info = f'&nbsp&nbsp&nbsp&nbsp [THREAD RES.] {msg_info}'
        return msg_info

    @staticmethod
    def msg_body(msg):
        """Construct body of message."""
        msg_body = f'» {msg.text}<br/><br/>'
        if msg.thread_child:
            msg_body = f'&nbsp&nbsp&nbsp&nbsp{msg_body}'
        return msg_body

    def msg_pg(self, msg):
        """Convert message info & body to PDF paragraph object."""
        msg_info = self.msg_info(msg)
        msg_body = self.msg_body(msg)
        msg_info_pg = Paragraph(msg_info, self.msg_info_style)
        msg_body_pg = Paragraph(msg_body, self.msg_body_style)
        return msg_info_pg, msg_body_pg

    def print_pdf(self, convo_types):
        """Format & print PDF files for each convo-type."""
        for convo_type in convo_types:
            try:
                convo_attr = getattr(self, convo_type)
            except AttributeError:
                continue
            else:
                pdf = self.create_blank_pdf(convo_type)
                setattr(self, 'pdf_content', [])
                for day in convo_attr:
                    date_heading = self.date_heading(convo_type, day.date)
                    date_heading_pg = Paragraph(date_heading, self.date_heading_style)
                    self.pdf_content.append(date_heading_pg)
                    for convo in day.convos:
                        msg_heading = self.msg_heading(convo, convo_type)
                        msg_heading_pg = Paragraph(msg_heading, self.msg_heading_style)
                        self.pdf_content.append(msg_heading_pg)
                        for msg in convo.messages:
                            msg_info_pg, msg_body_pg = self.msg_pg(msg)
                            self.pdf_content.append(msg_info_pg)
                            self.pdf_content.append(msg_body_pg)

                pdf.build(self.pdf_content)

    @staticmethod
    def make_dir():
        """Create directory on desktop of user for PDF files."""
        desktop = f'{os.path.expanduser("~")}/Desktop'
        slack_dir = f'{desktop}/Slack Output'
        os.makedirs(slack_dir, exist_ok=True)
        os.chdir(slack_dir)
        click.launch(slack_dir)

