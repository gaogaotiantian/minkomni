import discord
from .firebase_proxy import fb_get, fb_set

from .bot import bot


@bot.hybrid_command()
async def addcharacter(ctx, member: discord.Member, character: str):
    """Adds a character to a member."""
    characters = fb_get(member, "characters")

    if characters:
        characters.append(character)
    else:
        characters = [character]

    fb_set(member, "characters", characters)

    await ctx.send(f'为{member.display_name}增加了角色"{character}"， 现在TA的角色有：{", ".join(characters)}')


@bot.hybrid_command()
async def deletecharacter(ctx, member: discord.Member, character: str):
    """Deletes a character from a member."""
    characters = fb_get(member, "characters")

    if characters and character in characters:
        characters.remove(character)
        fb_set(member, "characters", characters)
        await ctx.send(f'删除了{member.display_name}的角色"{character}", 现在TA的角色有：{", ".join(characters)}')
    else:
        await ctx.send(f'没有找到属于{member.display_name}的角色"{character}"')


@bot.hybrid_command()
async def querycharacter(ctx, member: discord.Member):
    """Queries characters of a member."""
    characters = fb_get(member, "characters")
    if characters:
        await ctx.send(f'{member.display_name}的角色有：{", ".join(characters)}')
    else:
        await ctx.send(f'没有找到属于{member.display_name}的角色')


@bot.hybrid_command()
async def listvoicechannelcharacter(ctx, channel: discord.VoiceChannel):
    """Lists characters for all members in the voice channel."""
    if not channel.members:
        await ctx.send(f'{channel}里没人啊')
    else:
        ret = ""
        for member in channel.members:
            characters = fb_get(member, "characters")
            if characters:
                ret += f'{member.display_name}的角色有：{", ".join(characters)}\n'
            else:
                ret += f'没有找到属于{member.display_name}的角色\n'
        await ctx.send(ret)

