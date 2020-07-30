from discord.ext import commands
import discord
JA_VOICE_TYPES = "ABCD"
EN_VOICE_TYPES = "ABCDEF"


how_to_change = """
** 音声種類の変更コマンド **
`{prefix}voice [{ja}]` 日本語の音声設定を変更します。デフォルトはAです。
`{prefix}voice en [{en}]` 英語の音声設定を変更します。デフォルトはAです。

** ピッチの変更コマンド **
`{prefix}pitch <-6.5~6.5>` ピッチを変更します。デフォルトは0です。引数を渡さなかった場合デフォルトに変更されます。

** スピードの変更コマンド **
`{prefix}speed <0.5~4.0>` スピードを変更します。デフォルトは1です。引数を渡さなかった場合デフォルトに変更されます。
"""


async def refresh(bot, ctx, document):
    bot.guild_settings.set(ctx.author.id,
                           await document.data()
                           )


def get_types_text(types, with_lower=True):
    if with_lower:
        return f"{', '.join(t.lower() for t in types)}, {', '.join(t for t in types)}"

    return f"{', '.join(t for t in types)}"


async def edit_voice_type(bot, ctx, language, voice_type):
    document = bot.firestore.user.get(ctx.author.id)
    data = await document.data()
    await document.edit(voice={language: voice_type})
    await refresh(bot, ctx, document)
    await ctx.send(f'{ctx.author.mention}, {language}のボイスの設定を{data.voice[language]}から{voice_type}に変更しました。')


async def en_setting(bot, ctx, voice_type):
    if voice_type.upper() not in EN_VOICE_TYPES:
        await ctx.send(f"ボイスの設定は`{get_types_text(EN_VOICE_TYPES)}`から選んでください。")
        return

    await edit_voice_type(bot, ctx, 'en', voice_type.upper())


async def ja_setting(bot, ctx, voice_type):
    if voice_type.upper() not in JA_VOICE_TYPES:
        await ctx.send(f"ボイスの設定は`{get_types_text(JA_VOICE_TYPES)}`から選んでください。")
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
                          f"スピード: {data.speed}",
                    inline=False
                    )
    embed.add_field(name='設定コマンド',
                    value=how_to_change.format(prefix=ctx.prefix,
                                               ja=get_types_text(
                                                   JA_VOICE_TYPES, False),
                                               en=get_types_text(EN_VOICE_TYPES, False)),
                    inline=False
                    )

    await ctx.send(embed=embed)


async def change_pitch(bot, ctx, pitch):
    document = bot.firestore.user.get(ctx.author.id)
    data = await document.data()
    await document.edit(pitch=pitch)
    await refresh(bot, ctx, document)
    await ctx.send(f'{ctx.author.mention}, ピッチを{data.pitch}から{pitch}に変更しました。')


async def change_speed(bot, ctx, speed):
    document = bot.firestore.user.get(ctx.author.id)
    data = await document.data()
    await document.edit(speed=speed)
    await refresh(bot, ctx, document)
    await ctx.send(f'{ctx.author.mention}, ピッチを{data.speed}から{speed}に変更しました。')


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

    @commands.command()
    async def pitch(self, ctx, pitch: float = 0.0):
        if pitch < -6.5 or 6.5 < pitch:
            await ctx.send('ピッチは-6.5から6.5の間で指定してください。')
            return

        await change_pitch(self.bot, ctx, pitch)

    @commands.command(aliases=['rate'])
    async def speed(self, ctx, speed: float = 1.0):
        if speed < 0.5 or 4.0 < speed:
            await ctx.send('スピードは0.5から4.0の間で指定してください。')
            return

        await change_speed(self.bot, ctx, speed)


def setup(bot):
    return bot.add_cog(UserSetting(bot))
