import discord

from .bot import bot
from .firebase_proxy import fb_get

@bot.hybrid_command()
async def listvoicechannelinfo(ctx, channel: discord.VoiceChannel):
    """Lists characters for all members in the voice channel."""
    if not channel.members:
        await ctx.send(f'{channel}里没人啊')
    else:
        ret = ""
        for member in channel.members:
            timezone = fb_get(member, "timezone") or "未知"
            characters = fb_get(member, "characters")
            if characters:
                ret += f'{member.display_name}（{timezone}）的角色有：{", ".join(characters)}\n'
            else:
                ret += f'没有找到属于{member.display_name}（{timezone}）的角色\n'
        await ctx.send(ret)
