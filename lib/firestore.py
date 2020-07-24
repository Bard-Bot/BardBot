import firebase_admin
from firestore_guild import Guild
from firestore_guild_setting import Setting
from firebase_admin import credentials
from firebase_admin import firestore
import os
import concurrent.futures

cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

# TODO: credentialsをasyncio対応にする
firebase_admin.initialize_app(cred)


class FireStore:
    def __init__(self, bot):
        """
        プランと残り文字数、プランへお金を出した人を保存する
        :param bot: discord.ext.commands.Bot
        """
        self.bot = bot
        self.db = firestore.client()
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=20)
        self.guild = Guild(self)
        self.setting = Setting(self)
