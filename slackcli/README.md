# Slack CLI

The Slack CLI tool can be used to convert Slack workspace exports `(.zip)` to PDF files. It can also retrieve info for public/private channels and users utilizing Slack APIs.

### Requirements
Slack CLI requires `Python 3.7` or higher. See `requirements.txt` for dependencies.

### Installation

From terminal run the following commands.

```bash
brew install pipx
pipx ensurepath
```

Clone/Download files from repo and save to any directory. Navigate to that directory in terminal and run the following command below.

```bash
pipx install .
```

### Enviroment Variables
To use the User & Channel commands you will need the Slack token.

Once you have the token you will need to add it to your zsh profile. Open 
~/.zshrc in terminal and add the following line:
```
export SLACK_CLI_API="{token}"
```


### Usage
From any directory in terminal you can access the help menu by entering `slack`. The following commands are below.


##### slack export [FILEPATH] [OPTIONS] -u [USER EMAIL] -c [CHANNEL NAME] -d [DATE RANGE]

```
slack export ~/Desktop/file.zip -u dakota@company.co -c _it_all -d 01/01/2020 02/02/2020
```

>Using all 3 options would output a PDF of conversations within 
the specified date range from channel `_it_all` if the user `dakota@company.co`
was active or mentioned in it. 


```
slack export ~/Desktop/file.zip -u bob@company.co
```
> Using only the user option would output PDFs of all conversations
(DMs, MPDMs, Private / Public channels) the user `bob@company.co`
was apart of / active in for the entire date range of the zip file.


```
slack export ~/Desktop/file.zip -c general
```
> Using only the channel option would output a PDF of the channel
`general` history for the entire date range of the zip file.

```
slack export ~/Desktop/file.zip -d 06/17/2019 01/01/2020
```
> Using only the date range option would output PDFs for
all Private/Public channels within the specified date range.



##### slack user [EMAIL or ID]
```
slack user harrison@company.co
slack user AE2335H6
```


> The user command will return the users Slack profile info. Name, Slack ID, Admin Status, Owner Status.


##### slack channel [NAME or ID]
```
slack channel _it_all
slack channel H234DTR4
```
>The channel command will return the specified channels info. Name, Slack ID, Type, Num of Members, List of all members (full name, email).
