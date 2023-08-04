import os

# Really just make sure the modules run
from .activity import *
from .admin import *
from .bot import bot
from .character import *
from .info import *
from .item import *
from .server_check import *
from .timezone import *


class DiscordClient:
    async def start(self):
        token = os.getenv("DISCORD_BOT_TOKEN")
        if token:
            await bot.start(token)
