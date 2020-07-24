from os import environ
from os.path import join, dirname
from dotenv import load_dotenv

from bot import BardBot

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


bot = BardBot()


extensions = ['cogs.reload']

for extension in extensions:
    bot.load_extension(extension)

bot.run(environ.get('TOKEN'))
