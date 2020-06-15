import argparse
import sys


class Args:
    """Class that represents an ARGPARSE object."""
    def __init__(self):
        """Initialize instance of ARGPARSE class."""
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()
        self.add_command_arguments()
        self.values = self.parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    def add_command_arguments(self):
        # Create user command
        create_parser = self.subparsers.add_parser('create_user', help='Create a user in GSuite.')
        create_parser.set_defaults(create_user=True, sync_users=False)
        create_parser.add_argument('email', type=str.lower, help='Email of user to create.')
        create_parser.add_argument('country', type=str.lower, help='Country where user is based.')
        create_parser.add_argument('office', type=str.lower, help='Office where user is based.')
        create_parser.add_argument('-m' , '--manager', action='store_true', help='If user is a Manager.')
        create_parser.add_argument('-b', '--business', action='store_true', help='Users business org.')
        create_parser.add_argument('--test', action='store_true', help='Execute a test run of func.')

        # Sync users command
        sync_parser = self.subparsers.add_parser('sync_users', help='Sync users between FreshService & GSuite.')
        sync_parser.set_defaults(sync_users=True, create_user=False)
        sync_parser.add_argument('--test', action='store_true', help='Execute a test run of func.')
