from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
import sentry_sdk
from bot import BardBot

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


bot = BardBot()


extensions = [
    'cogs.reload',
    'cogs.user_setting',
    'cogs.guild_setting',
    'cogs.voice',
    'cogs.text_to_speech',
    'cogs.guild_dict',
    'cogs.admin',
    'cogs.help',
    'cogs.ad',
]

for extension in extensions:
    bot.load_extension(extension)

try:
    bot.run(environ.get('TOKEN'))
except RuntimeError as e:
    if str(e) != "Event loop stopped before Future completed.":
        sentry_sdk.capture_exception(e)
except Exception as e:
    sentry_sdk.capture_exception(e)
