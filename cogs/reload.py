from discord.ext import commands
from typing import TYPE_CHECKING
from dataclasses import dataclass
if TYPE_CHECKING:
    from bard import BardBot

owner_ids = [
    212513828641046529,
]


@dataclass
class Reload(commands.Cog):
    bot: 'BardBot'

    def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.author.id not in owner_ids:
            return False
        return True

    @commands.group(invoke_without_command=True)
    async def reload(self, ctx: commands.Context, name: str) -> None:
        self.bot.reload_extension(name)

        await ctx.send(f'reload extension: {name}')

    @reload.command()
    async def all(self, ctx: commands.Context) -> None:
        for extension in list(self.bot.extensions):
            self.bot.reload_extension(extension)

        await ctx.send('Reloaded all extensions.')


def setup(bot: 'BardBot'):
    return bot.add_cog(Reload(bot))
