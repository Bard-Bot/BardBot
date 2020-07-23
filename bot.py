from discord.ext import commands
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ',
            f'<@{user_id}> ',
            environ.get('prefix', '::'),
            'bard::',
            ]

    return base


class BardBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, help_command=None)
