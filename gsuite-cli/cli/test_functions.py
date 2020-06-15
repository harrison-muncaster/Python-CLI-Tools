import json


def sync_users(fresh, gsuite):
    """This function is for testing the functionality of the syncUsers command without making actual API calls.
    Prints would be results of running main function."""
    unique_users = fresh.users ^ gsuite.users
    print('Testing sync_users command...')
    for user in unique_users:
        if user not in fresh.users:
            if user in fresh.agents:
                print(f'Skipping {user}. This user is a FreshService agent.')
                continue
            print(f'Added {user} to FreshService.')

        else:
            print(f'Deleted {user} from FreshService.')


def create_user(args, gsuite):
    """This function is for testing the functionality of the createUser command. Will create a user in
    the sandbox domain. Prints would be results of running main function."""
    arg = args.values
    print('Testing create_user command...')
    if '.' not in arg.email or '@' not in arg.email:
        args.parser.error('Email must be in "firstname.lastname@company.com" format.')

    user = gsuite.create_user()
    print(f'User {arg.email} created.')
    generate_codes = gsuite.generate_verification_codes()

    #  Open groups JSON file to determine groups user should be added to
    with open('../templates/test_groups.json', 'r') as groups_json:
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
