from discord.ext import commands
import discord
from lib import color


def t_or_f(t):
    return '読み上げる' if t else '読み上げない'


how_to_change = """
`{prefix}pref name`  => ユーザーの名前を読み上げるか設定します。デフォルト: 読み上げる
`{prefix}pref emoji` => 絵文字を読み上げるか設定します。デフォルト: 読み上げる
`{prefix}pref bot`   => Botのメッセージを読み上げるか設定します。デフォルト: 読み上げない
`{prefix}pref keep`  => 何かしらの要因でBotが強制的にボイスチャンネルから切断された場合、再接続するか設定します。デフォルト: 再接続する
`{prefix}pref limit [読み上げる文字数]` => 読み上げる最大文字数を設定します。デフォルト: 100文字
"""


class GuildSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def refresh(self, ctx, document):
        self.bot.guild_settings.set(ctx.guild.id,
                                    await document.data()
                                    )

    @commands.group(invoke_without_command=True, aliases=['setting', 'preference'])
    async def pref(self, ctx):
        """ギルドの設定を表示"""
        data = await self.bot.firestore.setting.get(ctx.guild.id).data()
        embed = discord.Embed(title=f"{ctx.guild.name} のサーバー設定",
                              color=color.default)
        embed.add_field(name='ユーザーの名前', value=t_or_f(data.name), inline=False)
        embed.add_field(name='絵文字', value=t_or_f(data.emoji), inline=False)
        embed.add_field(name='Botのメッセージ', value=t_or_f(data.bot), inline=False)
        embed.add_field(name='再接続', value='する' if data.keep else 'しない', inline=False)
        embed.add_field(name='読み上げ上限', value=f'{data.limit}文字', inline=False)
        embed.add_field(name='設定コマンド', value=how_to_change.format(prefix=ctx.prefix), inline=False)

        await ctx.send(embed=embed)

    @pref.command()
    async def name(self, ctx):
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(name=not data.name)
        await self.refresh(ctx, document)
        await ctx.send(
            f'{ctx.author.mention}, 名前を `{t_or_f(data.name)}` から `{t_or_f(not data.name)}` に変更しました。'
        )

    @pref.command()
    async def emoji(self, ctx):
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.emoji)
        await self.refresh(ctx, document)
        await ctx.send(
            f'{ctx.author.mention}, 絵文字を `{t_or_f(data.emoji)}` から `{t_or_f(not data.emoji)}` に変更しました。'
        )

    @pref.command()
    async def bot(self, ctx):
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.bot)
        await self.refresh(ctx, document)
        await ctx.send(
            f'{ctx.author.mention}, Botのメッセージを `{t_or_f(data.bot)}` から `{t_or_f(not data.bot)}` に変更しました。'
        )

    @pref.command()
    async def limit(self, ctx, limit=100):
        if limit <= 0 or 2000 < limit:
            await ctx.send('文字数は1から2000の間で指定してください。')
            return
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(limit=limit)
        await self.refresh(ctx, document)
        await ctx.send(f'{ctx.author.mention}, 文字数制限を`{data.limit}`文字から`{limit}`文字に変更しました。')

    @pref.command()
    async def keep(self, ctx):
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.keep)
        b = '再接続する' if data.keep else '再接続しない'
        a = '再接続する' if (not data.keep) else '再接続しない'
        await self.refresh(ctx, document)
        await ctx.send(
            f'{ctx.author.mention}, 接続が切られても `{b}` から `{a}` に変更しました。'
        )


def setup(bot):
    return bot.add_cog(GuildSetting(bot))
