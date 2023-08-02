from discord.ext import commands

from .bot import bot
from .firebase_proxy import fb_activity_clear

@bot.command()
@commands.has_permissions(administrator=True)
async def synccommands(ctx):
    new_commands = await bot.tree.sync()
    await ctx.send(f"Synced commands - {new_commands}")


@bot.command()
@commands.has_permissions(administrator=True)
async def clearactivities(ctx):
    fb_activity_clear()
    await ctx.send(f"活动清除成功")
