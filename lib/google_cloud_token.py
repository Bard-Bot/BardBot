from gcloud.aio.auth.token import Token


class TokenGenerator:
    def __init__(self, path):
        self.generator = Token(service_file=path, scopes=["https://www.googleapis.com/auth/cloud-platform"])

    async def get(self):
        return await self.generator.get()
