import firebase_admin
from google.cloud.firestore_v1 import Increment
from functools import partial
from firebase_admin import credentials
from firebase_admin import firestore
import os
import concurrent.futures

cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)


class FireStore:
    def __init__(self, bot):
        """
        プランと残り文字数、プランへお金を出した人を保存する
        :param bot: discord.ext.commands.Bot
        """
        self.bot = bot
        self.db = firestore.client()
        self.guild_collection = self.db.collection('guilds')
        self.guild_setting_collection = self.db.collection('guild_setting')
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=20)

    def get_guild(self, guild_id):
        return self.guild_collection.document(str(guild_id))

    def get_guild_setting(self, guild_id):
        return self.guild_setting_collection.document(str(guild_id))

    async def exists(self, document):
        result = await self.bot.loop.run_in_executor(self.executor, document.get)

        return result.exists

    async def fetch_guild(self, guild_id):
        guild = self.get_guild(guild_id)
        result = await self.bot.loop.run_in_executor(self.executor, guild.get)

        return result.to_dict()

    async def fetch_guild_setting(self, guild_id):
        guild_setting = self.get_guild_setting(guild_id)
        result = await self.bot.loop.run_in_executor(self.executor, guild_setting.get)

        return result.to_dict()

    async def spend_char(self, guild_id, count):
        guild = await self.get_guild(guild_id)
        if guild['count'] - count < 0:
            await self.bot.loop.run_in_executor(self.executor, partial(guild.set, {'count': 0}, merge=True))
            return False

        await self.bot.loop.run_in_executor(self.executor, partial(guild.set, {'count': Increment(-count)}, merge=True))
        return True
