import discord
from discord.ext import commands

from .bot import bot

@bot.command()
@commands.has_permissions(administrator=True)
async def synccommands(ctx):
    new_commands = await bot.tree.sync()
    await ctx.send(f"Synced commands - {new_commands}")
