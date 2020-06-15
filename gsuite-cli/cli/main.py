#!/usr/bin/env python3
"""
"""


import json

import test_functions as test
from fresh_service import FreshService
from gsuite import GSuite
from args import Args


args = Args()
arg = args.values
fresh = FreshService()
gsuite = GSuite(args)


def main():
    try:
        # Execution of script is a test
        if arg.test:
            if arg.sync_users:
                test.sync_users(fresh, gsuite)
            elif arg.create_user:
                test.create_user(args, gsuite)

        # Command is sync_users
        elif arg.sync_users:
            sync_users()

        # Command is create_user
        elif arg.create_user:
            create_users()

    except Exception as e:
        raise SystemExit(e)


def sync_users():
    """Sync users between FreshService & GSuite.
    """
    if len(gsuite.users) < 100:
        raise SystemExit('Error: Does not meet the minimum requirement of at least 100 GSuite users.')

    unique_users = fresh.users ^ gsuite.users  # Determine GSuite users not in FreshService & vice-versa
    for user in unique_users:
        if user not in fresh.users:  # User in GSuite but not in FS - add to FS
            if user in fresh.agents:  # User is a FreshService agent so skip user
                print(f'Skipping {user}. This user is a FreshService agent.')
                continue

            user_profile = gsuite.user_info(user)

            try:  # Add user to FreshService
                r = fresh.create_user(first_name=user_profile['name']['givenName'],
                                      last_name=user_profile['name']['familyName'],
                                      email=user_profile['primaryEmail'])
                if 'errors' in r:
                    raise Exception(r['errors'][0]['message'])
            except Exception as e:
                print(f'Cannot create user {user}. {e}')
            else:
                print(f'Added {user} to FreshService.')

        else:  # User in FreshService but not GSuite - delete user from FS
            user_id = fresh.lookup_user_by_email(user)['id']
            delete_user = fresh.delete_user(user_id)
            print(f'Deleted {user} from FreshService.')


def create_users():
    """Create a user in GSuite & add to relevant groups. Return Flashpaper link or
    write to console relevant info.
    """
    if '.' not in arg.email or '@' not in arg.email:
        args.parser.error('Email must be in "firstname.lastname@company.com" format.')

    user = gsuite.create_user()
    print(f'User {arg.email} created.')
    generate_codes = gsuite.generate_verification_codes()

    #  Open groups JSON file to determine groups user should be added to
    with open('../templates/groups.json', 'r') as groups_json:
        groups = json.load(groups_json)
    relevant_groups = [groups['country'][arg.country]]
    if arg.business:
        relevant_groups.append(groups['group'])
        relevant_groups.append(groups['group'][arg.office])
    if arg.manager:
        if arg.business:
            relevant_groups.append(groups['manager'])
    if arg.office != 'remote':
        relevant_groups.append(groups['office'][arg.office])

    # Add user to relevant GSuite groups
    for group in relevant_groups:
        add_to_group = gsuite.add_user_to_group(group)
        print(f'Added to {group}.')

    #  Generate Flashpaper links for user
    link = gsuite.generate_flashpaper_link()
    print(f'Link to credentials: {link}')


if __name__ == '__main__':
    main()
