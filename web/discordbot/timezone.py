import discord

from .bot import bot
from .firebase_proxy import fb_get, fb_set


@bot.hybrid_command()
async def settimezone(ctx, member: discord.Member, timezone: str):
    fb_set(member, "timezone", timezone)
    await ctx.send(f'为{member.display_name}设置了时区"{timezone}"')


@bot.hybrid_command()
async def querytimezone(ctx, member: discord.Member):
    timezone = fb_get(member, "timezone")
    if timezone:
        await ctx.send(f'{member.display_name}的时区是：{timezone}')
    else:
        await ctx.send(f'没有找到属于{member.display_name}的时区')
