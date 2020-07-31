import asyncio
import subprocess
import traceback
import textwrap
import io
from contextlib import redirect_stdout
from discord.ext import commands
import discord
import psutil
from lib.color import admin
from lib.embed import notice_embed


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    @commands.command(hidden=True)
    async def pull(self, ctx):
        await ctx.send('start pulling...')
        async with ctx.typing():
            stdout, stderr = await self.run_process('git pull')
            last = stderr[-1000:] if stderr else stdout[-1000:]
            content = '```\n' + last + '\n```'
            await ctx.send(content)

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    async def ainfo(self, ctx):
        embed = discord.Embed(title='admin info', color=admin)
        embed.add_field(
            name='ボイスチャンネル接続数',
            value=f'{len(self.bot.voice_manager.servers)}チャンネル',
            inline=False
        )
        embed.add_field(
            name='参加ギルド数',
            value=f'{len(self.bot.guilds)}ギルド',
            inline=False
        )
        mem = psutil.virtual_memory()
        embed.add_field(
            name='メモリー',
            value=f'メモリ使用率: {mem.percent}%\n使用メモリ量: {mem.used}\n空きメモリ量: {mem.available}',
            inline=False
        )
        cpu = psutil.cpu_percent(interval=1)
        embed.add_field(
            name='CPU',
            value=f'CPU使用率: {cpu}%'
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['exit', 'finish'])
    async def quit(self, ctx):
        text = 'Botが終了するため、１分後に読み上げが終了します。'
        for key, server in self.bot.voice_manager.servers.items():
            self.bot.loop.create_task(server.read_text_channel.send(embed=notice_embed(text, ctx)))

        await ctx.send(embed=notice_embed('１分後に終了します', ctx))
        await asyncio.sleep(60)

        for key, server in self.bot.voice_manager.servers.items():
            await server.close('Botが終了するため、読み上げが終了します...')

        await ctx.send(embed=notice_embed('終了します', ctx))
        await self.bot.close()


def setup(bot):
    return bot.add_cog(Admin(bot))
