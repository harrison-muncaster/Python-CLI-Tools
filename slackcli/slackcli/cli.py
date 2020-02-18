import click
from pyfiglet import Figlet
from zipfile import ZipFile

from slackcli.export import Pdf
from slackcli.slack_api import SlackAPI


def display(obj):
    """Format terminal marquee."""
    font = Figlet(font='Lean')
    marquee = {
        'slack': font.renderText('Slack'),
        'cli': '\tcommand line interface'
    }
    click.secho(f'{marquee["slack"]}', fg='bright_magenta', nl=False, bold=True)
    click.secho(f'{marquee["cli"]}', fg='cyan')
    click.secho('  ⱽᵉʳˢⁱᵒⁿ ¹⋅⁰ ᵇʸ ᴴᵃʳʳⁱˢᵒⁿ ᴹ⋅ ᶠᵒʳ ᴮⁱʳᵈ', fg='bright_black', dim=True)
    click.secho('⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻')
    return obj


def clear_line(status):
    """Clear terminal line in place & return cursur to start of line."""
    print(f'\r{len(status) * " "}', end='\r', flush=True)


@click.group()
@display
def cli():
    """
    > slack export --help

    > slack channel --help

    > slack user --help

    """
    pass


@cli.command()
@click.option('-u', '--user',
              help='Email address of user to extract messages from.')
@click.option('-d', '--dates',
              nargs=2,
              type=click.DateTime(formats=['%m/%d/%Y']),
              help='Date range to extract messages from (start date - end date). [FORMAT MM/DD/YYYY MM/DD/YYYY]')
@click.option('-c', '--channel',
              help='Channel name of specific private/public channel to extract.')
@click.argument('file', required=True, type=click.Path(exists=True))
@click.pass_context
def export(ctx, file, user, dates, channel):
    """[ARG] File Path [OPTIONS]"""
    if user:
        if '@' and '.' not in user:
            raise click.BadParameter('Input must be in the format of an email address.')
    if dates:
        if dates[0] > dates[1]:
            raise click.BadParameter('Start date must be before or equal to End date.')

    ctx.obj = Pdf(user, dates, channel)
    with ZipFile(file) as unzipped:
        ctx.obj.zip_file = unzipped
        status = 'Validating file & input..'
        click.secho(status, blink=True, nl=False)
        ctx.obj.validate_input()
        if ctx.obj.input_email and not ctx.obj.input_channel:
            convo_types = ['dms', 'mpims', 'groups', 'channels']
        else:
            convo_types = ['groups', 'channels']

        clear_line(status)
        status = 'Converting Slack export to PDF...'
        click.secho(status, blink=True, nl=False)
        ctx.obj.create_convo_objects(convo_types)
        ctx.obj.make_dir()
        ctx.obj.print_pdf(convo_types)
        clear_line(status)
        click.secho('PDF export Complete!')


@cli.command()
@click.argument('channel', required=True)
@click.pass_context
def channel(ctx, channel):
    """[ARG] Channel Name or ID"""
    ctx.obj = SlackAPI(channel=channel)
    val = False
    while not val:
        status = f'Looking up Slack channel {channel}...'
        click.secho(status, blink=True, nl=False)
        val = ctx.obj.complete_channel_info()

    clear_line(status)
    click.secho('Channel Details:\n⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻', fg='cyan')
    for key, value in val['info'].items():
        click.secho(f'{key}: ', fg='cyan', nl=False)
        click.secho(f'{value}', fg='white')
    click.secho('\nMembers: full name, email\n⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻', fg='cyan')
    for member in val['members']:
        click.secho(f'{member[0]}', fg='white', nl=False)
        click.secho(', ', fg='cyan', nl=False)
        click.secho(f'{member[1]}', fg='bright_white')


@cli.command()
@click.argument('user', required=True)
@click.pass_context
def user(ctx, user):
    """[ARG] User Email or ID"""
    ctx.obj = SlackAPI(user=user)
    data = False
    while not data:
        status = f'Looking up Slack user {user}...'
        click.secho(status, blink=True, nl=False)
        if '@' in user:
            data = ctx.obj.lookup_user_by_email()
        else:
            data = ctx.obj.lookup_user_by_id()
    clear_line(status)
    click.secho('User Details:\n⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻', fg='cyan')
    for key, value in data.items():
        click.secho(f'{key}: ', fg='cyan', nl=False)
        click.secho(f'{value}', fg='white')


