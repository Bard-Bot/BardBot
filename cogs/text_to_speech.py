from discord.ext import commands
import discord


class TextToSpeech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_message')
    async def text_to_speech(self, message: discord.Message):
        pass


def setup(bot):
    return bot.add_cog(TextToSpeech(bot))
