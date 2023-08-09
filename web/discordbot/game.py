import discord

from .bot import bot
from .games import Slots


@bot.hybrid_command()
async def newslots(ctx, bet: int):
    """新建一个摇摇水果机"""
    msg = await ctx.send("正在生成摇摇水果机...")
    slots = Slots(id=msg.id, bet=bet)
    await msg.edit(content=slots.content(), view=slots.view())

@bot.command()
async def clearslots(ctx):
    """清除所有闲置的摇摇水果机"""
    delete_count, left_count = Slots.clear()
    await ctx.send(f"清除完毕，清理了{delete_count}个闲置的摇摇水果机，还剩{left_count}个正在运行的摇摇水果机")
