from discord.ext import commands
import numpy as np
from lib import color
import discord
import asyncio


class Pagenator:
    def __init__(self, bot, ctx, data: dict):
        self.bot = bot
        self.data = data
        self.page = 0
        self.pages = np.array_split(list(data), 10)
        self.ctx = ctx
        self.message = None
        self.page_count = len(data) // 10 if not len(data) % 10 else len(data) // 10 + 1
        if self.page_count == 0:
            self.page_count = 1

    def get_embed(self):
        embed = discord.Embed(title="辞書一覧",
                              color=color.default,
                              timestamp=self.ctx.message.created_at
                              )
        for key in list(self.pages[self.page]):
            value = self.data[key]
            embed.add_field(name=key, value=value, inline=False)
        embed.set_footer(text=f'command by {self.ctx.author}', icon_url=self.ctx.author.avatar_url)
        embed.set_author(name=f'{self.page+1} / {self.page_count} ページ')
        return embed

    def check(self, reaction, user):
        emoji = str(reaction.emoji)
        return emoji in ["\U00002b05", "\U000027a1"] and user.id == self.ctx.author.id and reaction.message.id == self.message.id

    async def try_delete_reaction(self, emoji, user):
        if self.ctx.guild.me.guild_permissions.manage_messages:
            await self.message.remove_reaction(emoji, user)

    async def loop(self):
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

    async def start(self):
        embed = self.get_embed()
        self.message = await self.ctx.send(embed=embed)
        await self.message.add_reaction("\U00002b05")
        await self.message.add_reaction("\U000027a1")
        self.bot.loop.create_task(self.loop())


class GuildDict(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['dict'], invoke_without_command=True)
    async def word(self, ctx):
        """辞書のすべての内容を表示します"""
        document = self.bot.firestore.dict.get(ctx.guild.id)
        data = await document.data()
        pagenator = Pagenator(self.bot, ctx, data)
        await pagenator.start()

    @word.command(aliases=['put'])
    async def add(self, ctx, key, *, value):
        document = self.bot.firestore.dict.get(ctx.guild.id)
        await document.add(key, value)
        await ctx.send(f'{ctx.author.mention}, {key}を{value}として登録しました。')

    @word.command(aliases=['delete', 'del', 'pop'])
    async def remove(self, ctx, *, key):
        document = self.bot.firestore.dict.get(ctx.guild.id)
        await document.remove(key)
        await ctx.send(f'{ctx.author.mention}, {key}を削除しました。')


def setup(bot):
    return bot.add_cog(GuildDict(bot))
