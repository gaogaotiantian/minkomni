import discord

from .bot import bot
from .games import Slots


@bot.hybrid_command()
async def newslots(ctx, bet: int):
    """新建一个摇摇水果机"""
    msg = await ctx.send("正在生成摇摇水果机...")
    slots = Slots(id=msg.id, bet=bet)
    await msg.edit(content=slots.content(), view=slots.view())
