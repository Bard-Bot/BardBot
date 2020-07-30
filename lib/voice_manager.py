import sentry_sdk


class VoiceManager:
    def __init__(self, bot):
        self.bot = bot
        self.servers = {}

    def get(self, guild_id):
        return self.servers.get(guild_id, None)

    def set(self, guild_id, server):
        self.servers[guild_id] = server

    def delete(self, guild_id):
        try:
            del self.servers[guild_id]
        except KeyError:
            pass

    async def close(self, guild_id, text="読み上げを終了します。"):
        try:
            await self.servers[guild_id].close(text)
        except Exception as e:
            sentry_sdk.capture_exception(e)
        self.delete(guild_id)

    async def all_close(self, text="読み上げを終了します。"):
        for key in list(self.servers):
            server = self.servers[key]
            try:
                await server.close(text)
            except Exception as e:
                sentry_sdk.capture_exception(e)
            self.delete(key)
