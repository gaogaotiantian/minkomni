import discord

from .bot import bot
from .firebase_proxy import fb_get

@bot.hybrid_command()
async def listvoicechannelinfo(ctx, channel: discord.VoiceChannel):
    """列出所有在语音频道里的用户的角色信息"""
    if not channel.members:
        await ctx.send(f'{channel}里没人啊')
    else:
        ret = ""
        for member in channel.members:
            timezone = fb_get(member, "timezone") or "未知"
            characters = fb_get(member, "characters")
            if characters:
                ret += f'{member.mention}（{timezone}）的角色有：{", ".join(characters)}\n'
            else:
                ret += f'没有找到属于{member.mention}（{timezone}）的角色\n'
        await ctx.send(ret)
