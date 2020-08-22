from discord.ext import commands
import discord
from lib.voice_server import VoiceData
from typing import TYPE_CHECKING
from lib.firestore import UserSettingData, SettingData
from dataclasses import dataclass
if TYPE_CHECKING:
    from bard import BardBot


@dataclass
class TextToSpeech(commands.Cog):
    bot: 'BardBot'

    async def set_user_setting(self, user_id: int) -> UserSettingData:
        document = self.bot.firestore.user.get(user_id)
        data = await document.data()
        self.bot.user_settings.set(user_id, data)

        return data

    async def set_guild_setting(self, guild_id: int) -> SettingData:
        document = self.bot.firestore.setting.get(guild_id)
        data = await document.data()
        self.bot.guild_settings.set(guild_id, data)

        return data

    async def set_guild_dict(self, guild_id: int) -> dict:
        document = self.bot.firestore.dict.get(guild_id)
        data = await document.data()
        self.bot.guild_dicts.set(guild_id, data)

        return data

    async def say(self, message: discord.Message) -> None:
        user_setting = self.bot.user_settings.get(message.author.id) or await self.set_user_setting(message.author.id)
        guild_setting = self.bot.guild_settings.get(message.guild.id) or await self.set_guild_setting(message.guild.id)
        guild_dict = self.bot.guild_dicts.get(message.guild.id) or await self.set_guild_dict(message.guild.id)

        # bot
        if not guild_setting.bot and message.author.bot:
            return

        content = message.clean_content

        data = VoiceData(self.bot, message, content, guild_setting, user_setting, guild_dict)

        await self.bot.voice_manager.get(message.guild.id).put(data)

    @commands.Cog.listener(name='on_message')
    async def text_to_speech(self, message: discord.Message) -> None:
        if message.content.startswith(';'):
            return

        if message.guild is None:
            return

        if self.bot.voice_manager.get(message.guild.id) is None:
            return

        server = self.bot.voice_manager.get(message.guild.id)

        if server.read_text_channel.id != message.channel.id:
            return

        if (message.author.voice is None) or (message.author.voice.channel is None):
            return

        if message.author.voice.channel.id != server.send_voice_channel.id:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            return

        await self.say(message)


def setup(bot: 'BardBot'):
    return bot.add_cog(TextToSpeech(bot))
