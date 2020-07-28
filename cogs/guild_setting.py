from discord.ext import commands


def t_or_f(t):
    return '読み上げる' if t else '読み上げない'


class GuildSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_with_command=True, aliases=['setting', 'preference'])
    async def pref(self, ctx):
        """ギルドの設定を表示"""
        pass

    @pref.command()
    async def name(self, ctx):
        document = self.bot.firestore.guild.get(ctx.guild.id)
        data = await document.data()
        await document.edit(name=not data.name)
        await ctx.send(
            f'{ctx.author.mention}, 名前を `{t_or_f(data.name)}` から `{t_or_f(not data.name)}` に変更しました。'
        )

    @pref.command()
    async def emoji(self, ctx):
        document = self.bot.firestore.guild.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.emoji)
        await ctx.send(
            f'{ctx.author.mention}, 絵文字を `{t_or_f(data.emoji)}` から `{t_or_f(not data.emoji)}` に変更しました。'
        )

    @pref.command()
    async def bot(self, ctx):
        document = self.bot.firestore.guild.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.bot)
        await ctx.send(
            f'{ctx.author.mention}, Botのメッセージを `{t_or_f(data.bot)}` から `{t_or_f(not data.bot)}` に変更しました。'
        )

    @pref.command()
    async def limit(self, ctx, limit=100):
        if limit <= 0 or 2000 < limit:
            await ctx.send('文字数制限は1から2000の間で指定してください。')
            return
        document = self.bot.firestore.guild.get(ctx.guild.id)
        data = await document.data()
        await document.edit(limit=limit)
        await ctx.send(f'{ctx.author.mention}, 文字数制限を{data.limit}から{limit}に変更しました。')

    @pref.command()
    async def keep(self, ctx):
        document = self.bot.firestore.guild.get(ctx.guild.id)
        data = await document.data()
        await document.edit(emoji=not data.keep)
        b = '接続を保つ' if data.keep else '接続を保たない'
        a = '接続を保つ' if (not data.keep) else '接続を保たない'
        await ctx.send(
            f'{ctx.author.mention}, 接続が切られても `{b}` から `{a}` に変更しました。'
        )


def setup(bot):
    return bot.add_cog(GuildSetting(bot))
