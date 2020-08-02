import asyncio
from lib.text_to_speech import fetch_voice_data
import discord
import io
import audioop
import re
import sentry_sdk
import aiohttp
import emoji_data_python
from lib import color

LANGUAGE_COMPILE = re.compile(r'([a-zA-Z]{2})::(.+)')
LANGUAGES = {
    'ja': 'ja-JP',
    'en': 'en-US',
}


def convert_voice_name(language, name):
    return f'{language}-Wavenet-{name}'


class VoiceData:
    def __init__(self, bot, message, text, guild_setting, voice_setting, guild_dict):
        self.bot = bot
        self.message = message
        self._text = text
        self.guild_setting = guild_setting
        self.voice_setting = voice_setting
        self.guild_dict = guild_dict
        self.language = None

        self.set_language()

    def set_language(self):
        if match := LANGUAGE_COMPILE.match(self._text):
            groups = match.groups()
            self._text = groups[1]
            self.language = groups[0] if groups[0] in LANGUAGES.keys() else 'ja'
        else:
            self.language = 'ja'

    @property
    def text(self):
        return self._text

    async def source(self, session):
        data = await fetch_voice_data(
            session=session,
            token=self.bot.google_cloud_token,
            text=self.text,
            language_code=LANGUAGES[self.language],
            name=convert_voice_name(LANGUAGES[self.language], self.voice_setting.voice[self.language]),
            rate=self.voice_setting.speed,
            pitch=self.voice_setting.pitch,
        )
        source = discord.PCMAudio(io.BytesIO(audioop.tostereo(data, 2, 1, 1)))
        return discord.PCMVolumeTransformer(source, volume=0.4)

    def set_name(self, last_author_id):
        if not self.guild_setting.name:
            return self
        if self.message.author.id == last_author_id:
            return self
        name = self.message.author.nick or self.message.author.name
        self._text = name + ('、' if self.language == 'ja' else ',') + self._text

        return self

    def convert_emoji(self):
        if not self.guild_setting.emoji:
            self._text = re.sub(r"<a?:(.{1,32}):[0-9]{17,18}>", r"", self._text)

            emojis = emoji_data_python.get_emoji_regex().findall(self._text)
            for emoji in emojis:
                self._text = self._text.replace(emoji, '')

            return self
        self._text = re.sub(r"<a?:(.{1,32}):[0-9]{17,18}>", r"\1", self._text)

        return self

    def convert_w(self):
        if self.language != "ja":
            return self

        text = self._text
        text = re.sub(r"([^a-zA-Z])([w]+)([^a-zA-Z])", r"\1、わら、\3", text)
        text = re.sub(r"^([w]+)$", "わら", text)
        text = re.sub(r"^[笑]$", "わら", text)
        text = re.sub(r"([^a-zA-Z])([w]+)$", r"\1、わら", text)
        self._text = text
        return self

    def convert_md(self):
        self._text = re.sub(r'\|\|.+\|\|', ',', self._text)
        self._text = re.sub(r'~~(.+)~~', r'\1', self._text)
        self._text = re.sub(r'__(.+)__', r'\1', self._text)
        self._text = re.sub(r'_(.+)_', r'\1', self._text)
        self._text = re.sub(r'\*\*(.+)\*\*', r'\1', self._text)
        self._text = re.sub(r'```(.+)```', r'\1', self._text)
        self._text = re.sub(r'`(.+)`', r'\1', self._text)
        if self._text.startswith('>'):
            self._text = self._text.replace('>', '')
        return self

    def convert_url(self):
        url_text = "URL省略、" if self.language == "ja" else "URL,"
        self._text = re.sub(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+", url_text, self._text)
        return self

    def set_text_length(self):
        if len(self.text) > self.guild_setting.limit:
            self._text = self.text[:self.guild_setting.limit] + ('以下略' if self.language == 'ja' else 'omitted')

        return self

    def convert_guild_dict(self):
        for key, value in self.guild_dict.items():
            self._text = self._text.replace(key, value)
        return self

    async def is_spendable(self):
        document = self.bot.firestore.guild.get(self.message.guild.id)
        data = await document.data()
        r = data.is_spendable(len(self.text))
        if not r:
            new = {key: 0 for key in data.data.keys() if key != 'subscribe'}
            await document.set_data(new)

        return r

    async def spend_char(self):
        r = await self.bot.firestore.guild.get(self.message.guild.id).spend_char(len(self.text))
        if r is None:
            return False
        return True


class VoiceServer:
    def __init__(self, bot, send_voice_channel, read_text_channel, voice_client):
        self.bot = bot
        self.send_voice_channel = send_voice_channel
        self.read_text_channel = read_text_channel
        self.voice_client: discord.VoiceClient = voice_client
        self.queue = asyncio.Queue(maxsize=20, loop=bot.loop)
        self.last_author_id = None
        self.session = None
        self.task = self.bot.loop.create_task(self.loop())

    async def setup(self):
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        return True

    async def put(self, item):
        await self.queue.put(item)

    async def close(self, text="読み上げを終了します。", error=False):
        self.voice_client.stop()
        await self.session.close()
        try:
            await self.voice_client.disconnect(force=True)
        except Exception:
            pass
        self.task.cancel()
        if error:
            embed = discord.Embed(title='エラー',
                                  description=text,
                                  color=color.error)
            await self.read_text_channel.send(embed=embed)
        else:
            embed = discord.Embed(title='成功',
                                  description=text,
                                  color=color.success)
            await self.read_text_channel.send(embed=embed)
        self.bot.voice_manager.delete(self.read_text_channel.guild.id)

    async def move_voice_channel(self, new_voice_channel, new_text_channel):
        self.voice_client.stop()
        self.send_voice_channel = new_voice_channel
        self.read_text_channel = new_text_channel
        await self.voice_client.move_to(new_voice_channel)
        return True

    async def reconnect(self, channel):
        try:
            client = await channel.connect(timeout=5)
            self.send_voice_channel = channel
            self.voice_client = client
        except discord.ClientException:
            pass

    async def loop(self):
        try:
            while not self.bot.is_closed():
                item: VoiceData = await self.queue.get()
                item.convert_url().convert_emoji().convert_md().convert_w().set_name(
                    self.last_author_id).convert_guild_dict().set_text_length()

                if not await item.is_spendable():
                    await self.close("申し訳ございません。今月の利用可能文字数を超えてしまいました。\n"
                                     "まだご利用になりたい場合は、公式サイト( https://bardbot.net )より購入してください。", error=True)
                    return
                await item.spend_char()

                while self.voice_client.is_playing():
                    await asyncio.sleep(0.5, loop=self.bot.loop)
                await asyncio.sleep(0.2, loop=self.bot.loop)

                self.voice_client.play(await item.source(self.session))
                self.last_author_id = item.message.author.id

        except asyncio.CancelledError:
            pass

        except audioop.error as e:
            await self.close("内部エラーが発生しました。再接続してください。", error=True)
            sentry_sdk.capture_exception(e)

        except Exception as e:
            sentry_sdk.capture_exception(e)
            await self.close("内部エラーが発生しました。再接続してください。", error=True)
