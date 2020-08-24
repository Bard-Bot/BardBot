from functools import partial


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


class UserSettingSnapshot:
    def __init__(self, document, user_setting):
        self.document = document
        self.setting = user_setting
        self.executor = user_setting.executor
        self.bot = user_setting.bot

    async def data(self):
        result = await self.document.get()
        d = result.to_dict()
        if d is None:
            return await self.create()

        return UserSettingData(d)

    async def exists(self):
        result = await self.document.get()

        return result.exists

    async def create(self):
        if await self.exists():
            return
        payload = dict(
            voice=dict(ja='A', en='A'),  # グローバル設定
            pitch=0.0,
            speed=1.0,
        )

        await self.document.set(payload)
        return UserSettingData(payload)

    async def edit(self, voice=None, pitch=None, speed=None):
        base = await self.data()
        voice = base.voice if voice is None else voice
        pitch = base.pitch if pitch is None else pitch
        speed = base.speed if speed is None else speed

        payload = dict(voice=voice, pitch=pitch, speed=speed)

        await self.document.set(payload, merge=True)


class UserSetting:
    def __init__(self, firestore):
        self.bot = firestore.bot
        self.firestore = firestore
        self.db = firestore.db
        self.executor = firestore.executor
        self.collection = self.db.collection('user_setting')

    def get(self, guild_id):
        return UserSettingSnapshot(self.collection.document(str(guild_id)), self)
