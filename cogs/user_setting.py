from discord.ext import commands
import discord
JA_VOICE_TYPES = "ABCD"
EN_VOICE_TYPES = "ABCDEF"


how_to_change = """
** 音声種類の変更コマンド **
`::voice [A, B, C, D]` で、日本語の音声設定を変更できます。
`::voice en [A, B, C, D]` で、英語の音声設定を変更できます。

** ピッチの変更コマンド **
`::pitch <-6.5~6.5>` ピッチを変更します。デフォルトは0です。

** スピードの変更コマンド **
`::speed <0.5~4.0>` スピードを変更します。デフォルトは1です。
"""


def get_types_text(types):
    return f"{', '.join(t.lower() for t in types)},{', '.join(t for t in types)}"


async def edit_voice_type(bot, ctx, language, voice_type):
    document = bot.firestore.user.get(ctx.author.id)
    data = await document.data()
    await document.edit(voice={language: voice_type})

    await ctx.send(f'{ctx.author.mention}, {language}のボイスの設定を{data.voice[language]}から{voice_type}に変更しました。')


async def en_setting(bot, ctx, voice_type):
    if voice_type.upper() not in EN_VOICE_TYPES:
        await ctx.send(f"ボイスの設定は{get_types_text(EN_VOICE_TYPES)}から選んでください。")
        return

    await edit_voice_type(bot, ctx, 'en', voice_type.upper())


async def ja_setting(bot, ctx, voice_type):
    if voice_type.upper() not in JA_VOICE_TYPES:
        await ctx.send(f"ボイスの設定は{get_types_text(JA_VOICE_TYPES)}から選んでください。")
        return

    await edit_voice_type(bot, ctx, 'ja', voice_type.upper())


async def show_voice_setting(bot, ctx):
    document = bot.firestore.user.get(ctx.author.id)
    data = await document.data()
    embed = discord.Embed(
        title=f'{ctx.author}の音声設定',
        color=discord.Color.from_rgb(25, 118, 210)
    )
    embed.add_field(name="音声設定",
                    value=f"日本語のボイスの種類: {data.voice['ja']}\n"
                          f"英語のボイスの種類: {data.voice['en']}\n"
                          f"ピッチ: {data.pitch}\n"
                          f"スピード: {data.speed}"
                    )
    embed.add_field(name='設定コマンド', value=how_to_change)

    await ctx.send(embed=embed)


class UserSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def voice(self, ctx, voice_type=None):
        """ボイスの設定一覧表示"""
        if voice_type is None:
            await show_voice_setting(self.bot, ctx)
            return

        await ja_setting(self.bot, ctx, voice_type)

    @voice.command()
    async def en(self, ctx, voice_type=None):
        """英語の設定"""
        if voice_type is None:
            await show_voice_setting(self.bot, ctx)
            return

        await en_setting(self.bot, ctx, voice_type)


def setup(bot):
    return bot.add_cog(UserSetting(bot))
