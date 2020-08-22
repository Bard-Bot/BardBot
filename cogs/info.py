from discord.ext import commands
from typing import TYPE_CHECKING
from dataclasses import dataclass
import discord
from lib.embed import set_meta
from lib.color import default
from lib.voice_server import VoiceServer

if TYPE_CHECKING:
    from bard import BardBot


@dataclass
class Info(commands.Cog):
    bot: 'BardBot'

    @commands.command()
    async def info(self, ctx: commands.Context) -> None:
        """現在の登録状況などを表示します。"""
        data = await self.bot.firestore.guild.get(ctx.guild.id).data()
        subscriptions = {key: value for key, value in data.data.items() if key not in ['count', 'subscribe']}
        embed = discord.Embed(
            title=f"{ctx.guild.name} の情報",
            color=default
        )
        embed.add_field(
            name="サブスクリプションに登録しているか",
            value="はい" if subscriptions else "いいえ",
            inline=False
        )
        embed.add_field(
            name="現在の残り文字数",
            value=f"{data.count}文字",
            inline=False
        )
        if subscriptions:
            embed.add_field(
                name="サブスクリプションの数",
                value=f"{len(subscriptions)}個",
                inline=False
            )
        await ctx.send(
            embed=set_meta(embed, ctx)
        )

    @commands.command()
    async def status(self, ctx: commands.Context) -> None:
        """現在のボイスの状態（接続先など）を表示する"""
        server: VoiceServer = self.bot.voice_manager.get(ctx.guild.id)

        embed = discord.Embed(
            title=f"{ctx.guild.name}の状況",
            description="Botが接続されているチャンネルなどを表示します。",
            color=default
        )
        if server is None:
            embed.add_field(
                name="接続状況",
                value="接続されていません。",
                inline=False
            )
            await ctx.send(embed=set_meta(embed, ctx))
            return
        embed.add_field(
            name="音声接続先のチャンネル",
            value=f"{server.send_voice_channel.mention}",
            inline=False
        )
        embed.add_field(
            name="テキスト接続先のチャンネル",
            value=f"{server.read_text_channel.mention}",
            inline=False
        )
        await ctx.send(embed=set_meta(embed, ctx))


def setup(bot: 'BardBot') -> None:
    return bot.add_cog(Info(bot))
