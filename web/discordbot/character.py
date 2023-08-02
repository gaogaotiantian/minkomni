import discord
from .firebase_proxy import fb_get, fb_set

from .bot import bot


@bot.hybrid_command()
async def addcharacter(ctx, member: discord.Member, character: str):
    """为用户添加一个角色"""
    characters = fb_get(member, "characters")

    if characters:
        characters.append(character)
    else:
        characters = [character]

    fb_set(member, "characters", characters)

    await ctx.send(f'为{member.mention}增加了角色"{character}"， 现在TA的角色有：{", ".join(characters)}')


@bot.hybrid_command()
async def deletecharacter(ctx, member: discord.Member, character: str):
    """为用户删除一个角色"""
    characters = fb_get(member, "characters")

    if characters and character in characters:
        characters.remove(character)
        fb_set(member, "characters", characters)
        await ctx.send(f'删除了{member.mention}的角色"{character}", 现在TA的角色有：{", ".join(characters)}')
    else:
        await ctx.send(f'没有找到属于{member.mention}的角色"{character}"')


@bot.hybrid_command()
async def querycharacter(ctx, member: discord.Member):
    """查询用户的角色"""
    characters = fb_get(member, "characters")
    if characters:
        await ctx.send(f'{member.mention}的角色有：{", ".join(characters)}')
    else:
        await ctx.send(f'没有找到属于{member.mention}的角色')
