from functools import partial


class LocalUserSettingData:
    def __init__(self, guild_id, data):
        self.guild_id = guild_id
        self.data = data

    @property
    def voice(self):
        return self.data['voice']

    @property
    def pitch(self):
        return self.data['pitch']

    @property
    def speed(self):
        return self.data['speed']


class UserSettingData:
    def __init__(self, data):
        self.data = data

    @property
    def voice(self):
        return self.data['voice']

    @property
    def pitch(self):
        return self.data['pitch']

    @property
    def speed(self):
        return self.data['speed']

    def local(self, guild_id):
        if str(guild_id) not in self.data['local'].keys():
            return None
        return LocalUserSettingData(guild_id, self.data['local'][str(guild_id)])


class UserSettingSnapshot:
    def __init__(self, document, user_setting):
        self.document = document
        self.setting = user_setting
        self.executor = user_setting.executor
        self.bot = user_setting.bot

    async def data(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)
        d = result.to_dict()
        if d is None:
            return UserSettingData(await self.create())

        return UserSettingData(d)

    async def exists(self):
        result = await self.bot.loop.run_in_executor(self.executor, self.document.get)

        return result.exists

    async def create(self):
        if await self.exists():
            return
        payload = dict(
            voice='A',  # グローバル設定
            local={},  # ローカル設定
            pitch=0.0,
            speed=1.0,
        )

        await self.bot.loop.run_in_executor(self.executor, self.document.set, payload)
        return payload

    async def edit(self, voice=None, pitch=None, speed=None):
        base = await self.data()
        voice = base.voice if voice is None else voice
        pitch = base.pitch if pitch is None else pitch
        speed = base.speed if speed is None else speed

        payload = dict(voice=voice, pitch=pitch, speed=speed)

        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, payload, merge=True))

    async def edit_local(self, guild_id, voice=None, pitch=None, speed=None):
        base = await self.data()
        local = base.local(guild_id)
        voice = local.voice if voice is None else voice
        pitch = local.pitch if pitch is None else pitch
        speed = local.speed if speed is None else speed

        payload = dict(
            local={
                str(guild_id): dict(voice=voice, pitch=pitch, speed=speed)
            }
        )

        await self.bot.loop.run_in_executor(self.executor, partial(self.document.set, payload, merge=True))


class UserSetting:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('user_setting')

    def get(self, guild_id):
        return UserSettingSnapshot(self.collection.document(str(guild_id)), self)
