from discord.ext import commands
import discord
from lib.voice_server import VoiceData


class TextToSpeech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def set_user_setting(self, user_id):
        document = self.bot.firestore.user.get(user_id)
        data = await document.data()
        self.bot.user_settings.set(user_id, data)

        return data

    async def set_guild_setting(self, guild_id):
        document = self.bot.firestore.setting.get(guild_id)
        data = await document.data()
        self.bot.user_settings.set(guild_id, data)

        return data

    async def set_guild_dict(self, guild_id):
        document = self.bot.firestore.dict.get(guild_id)
        data = await document.data()
        self.bot.user_settings.set(guild_id, data)

        return data

    @commands.Cog.listener(name='on_message')
    async def text_to_speech(self, message: discord.Message):
        if self.bot.voice_manager.get(message.guild.id) is None:
            return

        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            return

        user_setting = self.bot.user_settings.get(message.author.id) or await self.set_user_setting(message.author.id)
        guild_setting = self.bot.guild_settings.get(message.guild.id) or await self.set_guild_setting(message.guild.id)
        guild_dict = self.bot.guild_dicts.get(message.guild.id) or await self.set_guild_dict(message.guild.id)

        # bot
        if not guild_setting.bot and message.author.bot:
            return

        content = message.clean_content

        data = VoiceData(self.bot, message, content, guild_setting, user_setting, guild_dict)

        await self.bot.voice_manager.get(message.guild.id).put(data)


def setup(bot):
    return bot.add_cog(TextToSpeech(bot))
