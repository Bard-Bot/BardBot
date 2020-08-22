from discord.ext import commands
import discord
from lib import color
from lib.checks import permit_by_role
from lib.embed import success_embed, error_embed, set_meta
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bard import BardBot


def t_or_f(t):
    return '読み上げる' if t else '読み上げない'


how_to_change = """
`{prefix}pref name`  => ユーザーの名前を読み上げるか設定します。デフォルト: 読み上げる
`{prefix}pref emoji` => 絵文字を読み上げるか設定します。デフォルト: 読み上げる
`{prefix}pref bot`   => Botのメッセージを読み上げるか設定します。デフォルト: 読み上げない
`{prefix}pref keep`  => 何かしらの要因でBotが強制的にボイスチャンネルから切断された場合、再接続するか設定します。デフォルト: 再接続する
`{prefix}pref limit [読み上げる文字数]` => 読み上げる最大文字数を設定します。デフォルト: 100文字
"""


@dataclass
class GuildSetting(commands.Cog):
    bot: 'BardBot'

    async def refresh(self, ctx, document) -> None:
        self.bot.guild_settings.set(
            ctx.guild.id,
            await document.data()
        )

    @commands.group(invoke_without_command=True, aliases=['setting', 'preference'])
    async def pref(self, ctx: commands.Context) -> None:
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

        await ctx.send(embed=set_meta(embed, ctx))

    @pref.command()
    @permit_by_role()
    async def name(self, ctx: commands.Context) -> None:
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(name=not data.name)
        await self.refresh(ctx, document)
        await ctx.send(
            embed=success_embed(f'名前を `{t_or_f(data.name)}` から `{t_or_f(not data.name)}` に変更しました。', ctx)
        )

    @pref.command()
    @permit_by_role()
    async def emoji(self, ctx: commands.Context) -> None:
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.emoji)
        await self.refresh(ctx, document)
        await ctx.send(
            embed=success_embed(f'絵文字を `{t_or_f(data.emoji)}` から `{t_or_f(not data.emoji)}` に変更しました。', ctx)
        )

    @pref.command()
    @permit_by_role()
    async def bot(self, ctx: commands.Context) -> None:
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(bot=not data.bot)
        await self.refresh(ctx, document)
        await ctx.send(
            embed=success_embed(f'Botのメッセージを `{t_or_f(data.bot)}` から `{t_or_f(not data.bot)}` に変更しました。', ctx)
        )

    @pref.command()
    @permit_by_role()
    async def limit(self, ctx: commands.Context, limit: int = 100) -> None:
        if limit <= 0 or 2000 < limit:
            await ctx.send(embed=error_embed('文字数は1から2000の間で指定してください。', ctx))
            return
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(limit=limit)
        await self.refresh(ctx, document)
        await ctx.send(embed=success_embed(f'文字数制限を`{data.limit}`文字から`{limit}`文字に変更しました。', ctx))

    @pref.command()
    @permit_by_role()
    async def keep(self, ctx: commands.Context) -> None:
        document = self.bot.firestore.setting.get(ctx.guild.id)
        data = await document.data()
        await document.edit(keep=not data.keep)
        b = '再接続する' if data.keep else '再接続しない'
        a = '再接続する' if (not data.keep) else '再接続しない'
        await self.refresh(ctx, document)
        await ctx.send(
            embed=success_embed(f'接続が切られても `{b}` から `{a}` に変更しました。', ctx)
        )


def setup(bot):
    return bot.add_cog(GuildSetting(bot))
