from .color import error, success
import discord


def set_meta(embed, ctx):
    embed.set_footer(text=f'command by {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.timestamp = ctx.message.created_at
    return embed


def success_embed(desc, ctx):
    embed = discord.Embed(title='成功',
                          description=desc,
                          color=success)
    return set_meta(embed, ctx)


def error_embed(desc, ctx):
    embed = discord.Embed(title='エラー',
                          description=desc,
                          color=error)
    return set_meta(embed, ctx)
