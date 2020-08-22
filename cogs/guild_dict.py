from discord.ext import commands
from lib import color
from lib.embed import error_embed, success_embed
import discord
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bard import BardBot


class Pagenator:
    def __init__(self, bot: 'BardBot', ctx: commands.Context, data: dict) -> None:
        self.bot = bot
        self.data = data
        self.page = 0
        self.ctx = ctx
        self.message = None
        self.page_count = len(data) // 10 if not len(data) % 10 else len(data) // 10 + 1
        if self.page_count == 0:
            self.page_count = 1

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(title="辞書一覧",
                              color=color.default,
                              timestamp=self.ctx.message.created_at
                              )
        for key in list(self.data)[self.page * 10: self.page * 10 + 10]:
            value = self.data[key]
            embed.add_field(name=key, value=value, inline=False)
        embed.set_footer(text=f'command by {self.ctx.author}', icon_url=self.ctx.author.avatar_url)
        embed.set_author(name=f'{self.page+1} / {self.page_count} ページ')
        return embed

    def check(self, reaction: discord.Reaction, member: discord.Member) -> bool:
        emoji = str(reaction.emoji)
        return emoji in ["\U00002b05", "\U000027a1"] and member.id == self.ctx.author.id and reaction.message.id == self.message.id

    async def try_delete_reaction(self, emoji: str, member: discord.Member) -> None:
        if self.ctx.guild.me.guild_permissions.manage_messages:
            await self.message.remove_reaction(emoji, member)

    async def loop(self) -> None:
        while not self.bot.is_closed():
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.check, timeout=60)
            except asyncio.TimeoutError:
                await self.message.remove_reaction("\U00002b05", self.ctx.guild.me)
                await self.message.remove_reaction("\U000027a1", self.ctx.guild.me)
                return

            emoji = str(reaction.emoji)
            if emoji == "\U00002b05":  # left
                if self.page != 0:
                    self.page -= 1

            elif emoji == "\U000027a1":  # right
                if self.page != self.page_count - 1:
                    self.page += 1

            await self.message.edit(embed=self.get_embed())
            await self.try_delete_reaction(emoji, user)

    async def start(self) -> None:
        embed = self.get_embed()
        self.message = await self.ctx.send(embed=embed)
        await self.message.add_reaction("\U00002b05")
        await self.message.add_reaction("\U000027a1")
        self.bot.loop.create_task(self.loop())


@dataclass
class GuildDict(commands.Cog):
    bot: 'BardBot'

    @commands.group(aliases=['dict'], invoke_without_command=True)
    async def word(self, ctx: commands.Context) -> None:
        """辞書のすべての内容を表示します"""
        document = self.bot.firestore.dict.get(ctx.guild.id)
        data = await document.data()
        pagenator = Pagenator(self.bot, ctx, data)
        await pagenator.start()

    @word.command(aliases=['put'])
    async def add(self, ctx: commands.Context, key: str, *, value: str) -> None:
        document = self.bot.firestore.dict.get(ctx.guild.id)
        await document.add(key, value)

        self.bot.guild_dicts.set(ctx.guild.id, await document.data())
        await ctx.send(embed=success_embed(f'{key}を{value}として登録しました。', ctx))

    @word.command(aliases=['delete', 'del', 'pop'])
    async def remove(self, ctx: commands.Context, *, key: str) -> None:
        document = self.bot.firestore.dict.get(ctx.guild.id)
        if not await document.remove(key):

            await ctx.send(embed=error_embed(f'{key}は存在しません。', ctx))
            return

        self.bot.guild_dicts.set(ctx.guild.id, await document.data())
        await ctx.send(embed=success_embed(f'{key}を削除しました。', ctx))


def setup(bot: 'BardBot') -> None:
    return bot.add_cog(GuildDict(bot))
