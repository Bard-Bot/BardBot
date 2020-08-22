from discord.ext import commands
from lib.embed import error_embed


def permit_by_role():
    async def predicate(ctx: commands.Context) -> bool:
        role = [r for r in ctx.guild.roles if r.name == "BardManager"]
        if not role:
            return True

        if ctx.author.guild_permissions.administrator:
            return True

        for role in ctx.author.roles:
            if role.name == "BardManager":
                return True

        await ctx.send(
            embed=error_embed("あなたは`BardManager` 役職を持っていないため、このコマンドを実行することができません。", ctx)
        )

        return False

    return commands.check(predicate)
