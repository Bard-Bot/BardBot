from discord.ext import commands
import discord
from lib.color import notice
from os import environ
from lib.embed import success_embed

bot_invite = "https://discord.com/api/oauth2/authorize?client_id=727687910643466271&permissions=11855936&scope=bot"
guild_invite = "https://discord.gg/QmCmMtp"
website = "https://bardbot.net/"


class Ad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in [
            '!sh s',
            '?summon',
            '!shr s',
            '!shg s',
        ]:
            data = await self.bot.firestore.guild.get(message.guild.id).data()
            if data.subscribe:
                return
            embed = discord.Embed(title='Bardを使用してみませんか?',
                                  description='Bardは、高音質を目指して作られた有料読み上げBotです。\n従来の無料のBotよりも綺麗な音声で読み上げることができます。\nまた、音声の種類を男の人の声や女の人の声といったものに変更できます。',
                                  color=notice
                                  )
            embed.add_field(
                name='URL一覧',
                value=f'[Botの導入URL]({bot_invite})\n [公式サーバー]({guild_invite})\n [ウェブサイト]({website})'
            )
            embed.set_footer(text=f'{environ.get("prefix")}noad コマンドを実行することで、このメッセージを表示させないようにできます。')
            await message.channel.send(embed=embed)

    @commands.command()
    async def noad(self, ctx):
        await self.bot.firestore.guild.get(ctx.guild.id).set_subscribe()
        await ctx.send(embed=success_embed('広告は表示されなくなりました。', ctx))


def setup(bot):
    return bot.add_cog(Ad(bot))
