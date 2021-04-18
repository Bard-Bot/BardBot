from discord.ext import commands
from lib.voice_server import VoiceServer
import discord
import asyncio
from lib.embed import error_embed, success_embed
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bard import BardBot


@dataclass
class Voice(commands.Cog):
    bot: 'BardBot'

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.firestore.guild.get(guild.id).create()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        if before.channel is None or after.channel is not None:
            return

        server = self.bot.voice_manager.get(member.guild.id)
        if server is None:
            return

        if member.id == member.guild.me.id:
            await server.close('強制的に切断されたため終了します。')
            return

        if server.send_voice_channel.id != before.channel.id:
            return

        if len(before.channel.members) == 1:
            if before.channel.members[0].id == member.guild.me.id:
                await server.close('誰もいなくなったので読み上げを終了します。')
                return

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        async with ctx.channel.typing():
            # サーバー内で既に利用されていた場合
            if self.bot.voice_manager.get(ctx.guild.id) is not None:
                await ctx.send(
                    embed=error_embed("このサーバー内で既に利用されています。moveコマンドを使用するか、切断してから再度お試しください。", ctx)
                )
                return

            # 実行したユーザーがVCにいない場合
            if (ctx.author.voice is None) or (ctx.author.voice.channel is None):
                await ctx.send(
                    embed=error_embed("ボイスチャンネルに接続した状態で実行してください。", ctx)
                )
                return

            # 残り文字数が足りているか
            data = await self.bot.firestore.guild.get(ctx.guild.id).data()
            if data.count == 0:
                await ctx.send(
                    embed=error_embed("今月の利用可能文字数を超えています。\nまだご利用になりたい場合は、公式サイトより購入してください。", ctx)
                )
                return

            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect(timeout=5.0)

            # ボイスサーバーの作成
            server = VoiceServer(self.bot, voice_channel, ctx.channel, voice_client)
            await server.setup()

            self.bot.voice_manager.set(ctx.guild.id, server)

            await ctx.send(embed=success_embed("接続しました。", ctx))
            await self.bot.get_channel(733199945930113074).send(f"{ctx.guild.name} が接続しました。")

            try:
                # 多くのbotがやってるからつけてみた
                await ctx.guild.me.edit(deafen=True)
            except Exception:
                pass

    @join.error
    async def join_error(self, ctx: commands.Context, exception: Exception) -> None:
        exception = getattr(exception, 'original', exception)

        if isinstance(exception, discord.ClientException):
            await ctx.send(embed=error_embed("このサーバー内で既に利用されています。moveコマンドを使用するか、切断してから再度お試しください。", ctx))

        elif isinstance(exception, asyncio.TimeoutError):
            await ctx.send(
                embed=error_embed('接続できませんでした。ユーザー数が埋まっている可能性があります。再度お試しください。', ctx)
            )

        else:
            await ctx.send(
                embed=error_embed('予期せぬエラーが発生しました。再度お試しください。それでも表示される場合は公式サポートサーバーよりご連絡ください。', ctx)
            )
            print(exception)

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        async with ctx.channel.typing():

            server = self.bot.voice_manager.get(ctx.guild.id)
            if server is None:
                await ctx.send(
                    embed=error_embed("このサーバーは接続されていません。", ctx)
                )
                return

            if (ctx.author.voice is None) or (ctx.author.voice.channel is None):
                await ctx.send(embed=error_embed("ボイスチャンネルに接続した状態で実行してください。", ctx))
                return

            if server.read_text_channel.id != ctx.channel.id:
                await ctx.send(
                    embed=error_embed('読み上げるチャンネルと同じチャンネルで実行してください。', ctx)
                )

            if ctx.author.voice.channel.id != server.send_voice_channel.id:
                await ctx.send(
                    embed=error_embed("Botと同じボイスチャンネルで実行してください。", ctx)
                )
                return

            # 処理を終了させる
            await self.bot.voice_manager.close(ctx.guild.id)

    @leave.error
    async def leave_error(self, ctx: commands.Context, exception: Exception) -> None:
        await ctx.send(
            embed=error_embed('予期せぬエラーが発生しました。再度お試しください。それでも表示される場合は公式サポートサーバーよりご連絡ください。', ctx)
        )
        print(exception)

    @commands.command()
    async def fleave(self, ctx: commands.Context) -> None:
        """強制的に終了させる"""
        server = self.bot.voice_manager.get(ctx.guild.id)
        if server is None:
            for client in self.bot.voice_clients:
                if client.guild.id == ctx.guild.id:
                    await client.disconnect()
        else:
            await self.bot.voice_manager.close(ctx.guild.id)

        await ctx.send(embed=success_embed('処理が完了しました。', ctx))

    @commands.command()
    async def move(self, ctx: commands.Context) -> None:
        """Botを移動させる"""
        async with ctx.channel.typing():
            server = self.bot.voice_manager.get(ctx.guild.id)
            if server is None:
                await ctx.send(embed=error_embed("このサーバーは接続されていません。", ctx))
                return

            if (ctx.author.voice is None) or (ctx.author.voice.channel is None):
                await ctx.send(embed=error_embed("ボイスチャンネルに接続した状態で実行してください。", ctx))
                return

            # VoiceClient.move_toを実行
            await server.move_voice_channel(ctx.author.voice.channel, ctx.channel)
            await ctx.send(embed=success_embed('移動しました。', ctx))

    @move.error
    async def move_error(self, ctx: commands.Context, exception: Exception) -> None:
        exception = getattr(exception, 'original', exception)

        if isinstance(exception, discord.ClientException):
            await ctx.send(embed=error_embed("失敗しました。もう一度実行してください。人数が埋まっているなどの理由が考えられます。", ctx))
        else:
            await ctx.send(
                embed=error_embed('予期せぬエラーが発生しました。再度お試しください。それでも表示される場合は公式サポートサーバーよりご連絡ください。', ctx)
            )
            print(exception)


def setup(bot):
    return bot.add_cog(Voice(bot))
