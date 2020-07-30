from discord.ext import commands


class GuildDict(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(GuildDict(bot))
