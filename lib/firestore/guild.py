from google.cloud.firestore_v1 import Increment
from functools import partial


class GuildData:
    def __init__(self, data):
        self.data = data

    @property
    def count(self):
        return sum(value for key, value in self.data.items() if key != 'subscribe')

    @property
    def subscribe(self):
        return self.data['subscribe']

    def is_spendable(self, count):
        return self.count - count >= 0


class GuildSnapshot:
    def __init__(self, document, guild):
        self.document = document
        self.guild = guild
        self.executor = guild.executor
        self.bot = guild.bot

    async def data(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return GuildData(result.to_dict())

    async def exists(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return result.exists

    async def set(self, count):
        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, {'count': count}, merge=True))

    async def create(self):
        """TODO: GuildにBotが入った時に実行する"""
        if await self.exists():
            return
        payload = dict(subscribe=0, count=1500)

        await self.bot.loop.run_in_executor(self.executor, self.document.set, payload)
        return GuildData(payload)

    async def spend_char(self, count):
        """使用可能文字数を減らす"""
        data = await self.data()
        data2 = {key: value for key, value in data.data.items() if key != 'subscribe' and value != 0}
        used_data = {}
        if not data2:
            return
        while count > 0:
            min_key = min(data2, key=data2.get)
            if count > data2[min_key]:
                count -= data2[min_key]
                used_data[min_key] = 0
                del data2[min_key]
                continue
            used_data[min_key] = Increment(-count)
            count = 0
        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, used_data, merge=True))

    async def set_data(self, new_data):
        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, new_data, merge=True))

    async def set_subscribe(self):
        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, {'subscribe': 1}, merge=True))


class Guild:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('guilds')

    def get(self, guild_id):
        return GuildSnapshot(self.collection.document(str(guild_id)), self)
