## GSuite Sync & User Creation
This tool can be used to create a user in GSuite or sync users from GSuite into FreshService.

## Requirements
**Docker**. To install run the following command below and then open the Docker application to finish setup.
> brew cask install docker

**Google Cloud Project**. Follow the below steps to setup a project in Google Cloud.
- Navigate to https://console.cloud.google.com/cloud-resource-manager, sign-in, click Create Project

- Click API & Services on the sidebar then select OAuth Consent Screen
- Select Internal for User Type
- Enter Onboarding-CLI for Application Name
- Save

- Select Credentials on the sidebar
- Click Create Credentials then select OAuth client ID
- Select Desktop app for Menu Application Type
- Enter Onboarding-CLI for Name
- Click OK

- Select Dashboard on the sidebar
- Click Enable APIS & Services
- Search for admin SDK
- Select Admin SDk
- Click Enable

- Select Credentials from the sidebar
- Click the download button for the OAuth credentials file

**FreshService API token**. Once you have the token you will need to base64 encode in the following format:
> {your_token}:{anything_goes_here}

You will then need to add it to your bashrc or zshrc file saved in the following variable.
> FRESH_API

## Setup
To setup, navigate to the directory where the repo was cloned & run the following command in terminal.

> . ./setup.sh

## Usage
To sync users into FreshService run the following command:
> sync_users

To run a test execution of the command append **--test** to the command.
> sync_users --test

To create a user in GSuite run the following command:
> create_user {firstname.lastname}
