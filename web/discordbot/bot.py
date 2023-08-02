import logging

import discord
from discord.ext import commands

from .firebase_proxy import fb_get


intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = commands.Bot(command_prefix='?', intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        timezone = fb_get(member, "timezone") or "未知"
        ret = f'欢迎{member.mention}（{timezone}）进入语音频道{after.channel.mention}\n'
        characters = fb_get(member, "characters")
        if characters:
            ret += f'{member.mention}的角色有：{", ".join(characters)}\n'
        else:
            ret += f'没有找到属于{member.mention}的角色\n'
        
        await member.guild.system_channel.send(ret)
