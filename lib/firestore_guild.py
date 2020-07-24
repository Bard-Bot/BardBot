from google.cloud.firestore_v1 import Increment
from functools import partial


class GuildSnapshot:
    def __init__(self, document, guild):
        self.document = document
        self.guild = guild
        self.bot = guild.bot

    async def data(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return result.to_dict()

    async def exists(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return result.exists

    async def create(self):
        """TODO: GuildにBotが入った時に実行する"""
        if await self.exists():
            return
        payload = dict(subscribe=0, count=1500)

        await self.bot.loop.run_in_executor(self.executor, self.document.set, payload)
        return payload

    async def spend_char(self, count):
        """成功した場合はTrue、文字数が足りなかった場合はFalseを返す"""
        guild = await self.data()
        if guild['count'] - count < 0:
            await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, {'count': 0}, merge=True))
            return False

        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, {'count': Increment(-count)}, merge=True))
        return True


class Guild:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('guilds')

    def get(self, guild_id):
        return GuildSnapshot(self.collection.document(str(guild_id)), self)
