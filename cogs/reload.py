from discord.ext import commands
owner_ids = [
    212513828641046529,
]


class Reload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx):
        if ctx.author.id not in owner_ids:
            return False
        return True

    @commands.group(invoke_without_command=True)
    async def reload(self, ctx, name):
        self.bot.reload_extension(name)

        await ctx.send(f'reload extension: {name}')

    @reload.command()
    async def all(self, ctx):
        for extension in list(self.bot.extensions):
            self.bot.reload_extension(extension)

        await ctx.send('Reloaded all extensions.')


def setup(bot: commands.Bot):
    return bot.add_cog(Reload(bot))
