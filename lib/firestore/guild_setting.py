class SettingData:
    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data['name']

    @property
    def emoji(self):
        return self.data['emoji']

    @property
    def bot(self):
        return self.data['bot']

    @property
    def limit(self):
        return self.data['limit']

    @property
    def keep(self):
        return self.data['keep']


class SettingSnapshot:
    def __init__(self, document, setting):
        self.document = document
        self.setting = setting
        self.executor = setting.executor
        self.bot = setting.bot

    async def data(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return SettingData(result.to_dict()) or await self.create()

    async def exists(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return result.exists

    async def create(self):
        if await self.exists():
            return
        payload = dict(
            name=True,
            emoji=True,
            bot=False,
            limit=100,
            keep=True
        )
        await self.bot.loop.run_in_executor(self.executor, self.document.set, payload)
        return SettingData(payload)

    async def edit(self, name=None, emoji=None, bot=None, limit=None, keep=None):
        data = await self.data()
        name = name if name is not None else data['name']
        emoji = emoji if emoji is not None else data['emoji']
        bot = bot if bot is not None else data['bot']
        limit = limit if limit is not None else data['limit']
        keep = keep if keep is not None else data['keep']

        payload = dict(name=name, emoji=emoji, bot=bot, limit=limit, keep=keep)

        await self.bot.loop.run_in_executor(self.executor, self.document.set, payload)


class Setting:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('guild_settings')

    def get(self, guild_id):
        return SettingSnapshot(self.collection.document(str(guild_id)), self)
