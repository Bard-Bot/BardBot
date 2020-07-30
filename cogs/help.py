from discord.ext import commands
import discord
from lib import color
from lib.embed import set_meta
bot_invite = "https://discord.com/api/oauth2/authorize?client_id=727687910643466271&permissions=11855936&scope=bot"
guild_invite = "https://discord.gg/QmCmMtp"
website = "https://bardbot.net/"
fields = [
    ["課金方法", f"[こちらのサイト]({website})に登録し、サーバーを選択してからサブスクリプションに登録してください。"],
    ["特殊機能", "`en::`を先頭につけると、英語で読み上げてくれます。"]
]


def get_info_embed(ctx):
    info_embed = discord.Embed(title='Bard - 有料読み上げBot -', color=color.default)
    info_embed.add_field(name='各種URL',
                         value=f"[**` Botの導入URL `**]({bot_invite})\n [**` 公式サーバー `**]({guild_invite})\n [**` ウェブサイト `**]({website})",
                         inline=False
                         )
    for field in fields:
        info_embed.add_field(name=field[0], value=field[1], inline=False)

    return set_meta(info_embed, ctx)


def get_help_embed(ctx):
    prefix = ctx.prefix
    cmds = [
        [f"{prefix}join", "ボイスチャンネルに接続します。"],
        [f"{prefix}leave", "ボイスチャンネルから切断します。"],
        [f"{prefix}move", "入っているボイスチャンネルを変更します。"],
        [f"{prefix}word", "カスタム辞書の一覧を表示します。"],
        [f"{prefix}word add <キー> <変換先の値>", "ユーザー辞書を設定します。設定した場合、キーを変換先の値として読みます。"],
        [f"{prefix}word remove <キー>", "ユーザー辞書を削除します。"],
        [f"{prefix}pref", "読み上げの設定を表示します。"],
        [f"{prefix}pref bot", "botの投稿も読み上げるかどうかを設定します。オンの時に実行するとオフに、オフの時に実行するとオンになります。"],
        [f"{prefix}pref name", "名前を読み上げるかどうかを設定します。オンの時に実行するとオフに、オフの時に実行するとオンになります。"],
        [f"{prefix}pref emoji", "絵文字を読み上げるかどうかを設定します。オンの時に実行するとオフに、オフの時に実行するとオンになります。"],
        [f"{prefix}pref limit <読み上げ上限文字数>", "最大読み上げ文字数を設定します。デフォルトは100です。"],
        [f"{prefix}pref keep-alive", "ラグなどで切断された際に、再接続するか設定します。強制終了した際も再接続します。オンの時に実行するとオフに、オフの時に実行するとオンになります。"],
        [f"{prefix}voice", "音声の設定を表示します。"],
        [f"{prefix}voice, {prefix}speed, {prefix}pitch", f"音声の種類を変更します。これらの使い方は`{prefix}voice`コマンドで表示された使用方法をご覧ください。"],
    ]
    embed = discord.Embed(
        title="コマンド一覧", description=f"プレフィックスは`{prefix}`です。", color=color.default
    )
    for cmd in cmds:
        embed.add_field(name=cmd[0], value=cmd[1], inline=False)

    return set_meta(embed, ctx)


def get_do_subscribe_embed(ctx):
    embed = discord.Embed(
        title='サブスクリプションに登録しませんか？',
        description='サブスクリプションに登録することで機能を使用可能になります。まず無料の3000文字を試してから、サブスクリプションに登録しましょう。0文字になると、使用できなくなります。',
        color=color.default
    )
    embed.add_field(
        name='サブスクリプションの登録方法',
        value='まず、[Webサイト](https://bardbot.net)に飛び、ユーザー登録をしましょう。\n'
              '次に、[ギルド一覧](https://bardbot.net/guilds)からサブスクリプションを設定したいギルドを選択します。\n'
              'その後、カード情報などを入力すれば、登録完了です。',
        inline=False
    )
    return set_meta(embed, ctx)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=get_info_embed(ctx))
        await ctx.send(embed=get_help_embed(ctx))
        data = await self.bot.firestore.guild.get(ctx.guild.id).data()
        if data.subscribe == 0:
            await ctx.send(embed=get_do_subscribe_embed(ctx))


def setup(bot):
    return bot.add_cog(Help(bot))
