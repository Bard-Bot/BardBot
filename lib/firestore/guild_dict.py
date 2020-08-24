from functools import partial


class GuildDictSnapshot:
    def __init__(self, document, guild_dict):
        self.document = document
        self.executor = guild_dict.executor
        self.guild_dict = guild_dict
        self.bot = guild_dict.bot

    async def data(self):
        result = await self.document.get()
        d = result.to_dict()
        if d is None:
            await self.add('bard', 'バード')
            return {'bard': 'バード'}

        return d

    async def exists(self):
        result = await self.document.get()

        return result.exists

    async def add(self, key, value):
        await self.document.set({key: value}, merge=True)

    async def remove(self, key):
        base_data = await self.data()
        if key not in base_data.keys():
            return False
        del base_data[key]

        return await self.document.set(base_data)


class GuildDict:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('guild_dict')

    def get(self, guild_id):
        return GuildDictSnapshot(self.collection.document(str(guild_id)), self)
