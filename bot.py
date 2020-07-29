import discord
from discord.ext import commands
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
from lib.firestore.firestore import FireStore
from lib.voice_manager import VoiceManager
from lib.google_cloud_token import TokenGenerator
import asyncio
import uvloop
import sentry_sdk
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
sentry_sdk.init(environ.get("sentry"))


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ',
            f'<@{user_id}> ',
            environ.get('prefix', '::'),
            'bard::',
            ]

    return base


class Storage:
    def __init__(self, key_type=int):
        self.storage = {}
        self.key_type = key_type

    def get(self, key):
        if not isinstance(key, self.key_type):
            raise KeyError(f'invalid key type: {type(key)}')

        return self.storage.get(key, None)

    def set(self, key, value):
        self.storage[key] = value


class BardBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, help_command=None,
                         loop=asyncio.get_event_loop())

        self.firestore = FireStore(self)
        self.google_cloud_token = None
        self.token_generator = TokenGenerator(environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        sentry_sdk.capture_exception(Exception("This is an example of an error message."))
        self.loop.create_task(self.google_cloud_token_loop())
        self.voice_manager = VoiceManager(self)

        # guild and user settings dict
        self.guild_settings = Storage()
        self.user_settings = Storage()

    async def on_command_error(self, context, exception):

        # ignore command.error
        if hasattr(context.command, 'on_error'):
            return
        if isinstance(exception, commands.CommandNotFound):
            return
        if isinstance(exception, commands.CommandOnCooldown):
            return
        if isinstance(exception, commands.BadArgument) or isinstance(exception, commands.BadUnionArgument):
            await context.send('引数の型が間違っています。ヘルプコマンドを参照してください。')
            return

        sentry_sdk.capture_exception(exception.original)

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Game(
                name=f"{environ.get('prefix', '::')}help | 読み上げBot"
            )
        )

    async def google_cloud_token_loop(self):
        while not self.is_closed():
            self.google_cloud_token = await self.token_generator.get()
            await asyncio.sleep(3000)
