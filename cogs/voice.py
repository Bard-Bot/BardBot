from discord.ext import commands
from lib.voice_server import VoiceServer
import discord
import asyncio
import sentry_sdk


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        async with ctx.channel.typing():
            try:

                # サーバーがすでに接続されていた場合
                if self.bot.voice_manager.get(ctx.guild.id) is not None:
                    await ctx.send("このサーバーはすでに接続されています。moveコマンドを使用するか、切断してください。")
                    return

                # 実行したユーザーがVCにいない場合
                if (ctx.author.voice is None) or (ctx.author.voice.channel is None):
                    await ctx.send("ボイスチャンネルに接続した状態で実行してください。")
                    return

                voice_channel = ctx.author.voice.channel
                voice_client = await voice_channel.connect(timeout=5.0)

                # 残り文字数が足りているか
                data = await self.bot.firestore.guild.get(ctx.guild.id).data()
                if data.count == 0:
                    await ctx.send("今月の利用可能文字数を超えています。\n"
                                   "まだご利用になりたい場合は、公式サイトより購入してください。")
                    return

                # ボイスサーバーの作成
                server = VoiceServer(self.bot, voice_channel, ctx.channel, voice_client)
                await server.setup()

                self.bot.voice_manager.set(ctx.guild.id, server)

                await ctx.send("接続しました。")

                try:
                    # 多くのbotがやってるからつけてみた
                    await ctx.guild.me.edit(deafen=True)
                except Exception:
                    pass

            except discord.ClientException:
                await ctx.send("このサーバーはすでに接続されています。moveコマンドを使用するか、切断してください。")

            except asyncio.exceptions.TimeoutError:
                await ctx.send('接続できませんでした。ユーザー数が埋まっている可能性があります。再度接続してください。')

            except Exception as e:
                await ctx.send('予期せぬエラーが発生しました。再度接続してください。エラー内容は運営に送信されます。')
                sentry_sdk.capture_exception(e)

    @commands.command()
    async def leave(self, ctx):
        async with ctx.channel.typing():
            try:
                server = self.bot.voice_manager.get(ctx.guild.id)
                if server is None:
                    await ctx.send("このサーバーは接続されていません。")
                    return

                if ctx.author.voice.channel.id != server.send_voice_channel.id:
                    await ctx.send("Botと同じボイスチャンネルで実行してください。")
                    return

                # 処理を終了させる
                await self.bot.voice_manager.close(ctx.guild.id)

            except Exception as e:
                self.bot.voice_manager.delete(ctx.guild.id)
                await ctx.send('予期せぬエラーが発生しました。再度接続してください。エラー内容は運営に送信されます。')
                sentry_sdk.capture_exception(e)

    @commands.command()
    async def move(self, ctx):
        """Botを移動させる"""
        async with ctx.channel.typing():
            try:
                server = self.bot.voice_manager.get(ctx.guild.id)
                if server is None:
                    await ctx.send("このサーバーは接続されていません。")
                    return

                if (ctx.author.voice is None) or (ctx.author.voice.channel is None):
                    await ctx.send("ボイスチャンネルに接続した状態で実行してください。")
                    return

                if ctx.author.voice.channel.id != server.send_voice_channel.id:
                    await ctx.send("Botと同じボイスチャンネルで実行してください。")
                    return

                # VoiceClient.move_toを実行
                await server.move_voice_channel(ctx.author.voice.channel)

            except discord.ClientException:
                await ctx.send("失敗しました。もう一度実行してください。人数が埋まっているなどの理由が考えられます。")
                return

            except Exception as e:
                await ctx.send('予期せぬエラーが発生しました。再度接続してください。エラー内容は運営に送信されます。')
                sentry_sdk.capture_exception(e)


def setup(bot):
    return bot.add_cog(Voice(bot))
