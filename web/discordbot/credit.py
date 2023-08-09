import discord

from .bot import bot
from .firebase_proxy import fb_get, fb_get_users, fb_set
from .games.steal import Steal, MultipleStealError


@bot.hybrid_command()
async def querycredit(ctx):
    """查询自己的分数"""
    credit = fb_get(ctx.author, "credit")
    if credit is None:
        credit = 50
        fb_set(ctx.author, "credit", credit)

    await ctx.send(f'你的分数是：{credit}', ephemeral=True)


@bot.hybrid_command()
async def creditranking(ctx):
    """查询分数排行"""
    users = fb_get_users()
    users = sorted(users.items(), key=lambda x: x[1].get("credit", 0), reverse=True)
    users = users[:10]
    ret = "\n".join([f"{i+1}. <@{user[0]}>: {user[1].get('credit', 0)}" for i, user in enumerate(users)])
    await ctx.send(ret)


@bot.hybrid_command()
async def stealcredit(ctx, target: discord.Member, amount: int):
    """偷窃其他人的分数"""
    credit = fb_get(target, "credit") or 0
    if credit < amount:
        await ctx.send(f"{target.mention}的分数不够，无法偷窃", ephemeral=True)
        return
    if credit <= 0:
        await ctx.send(f"你没有分数，没有资格进行偷窃！", ephemeral=True)
        return
    if amount < 1:
        await ctx.send(f"一次至少偷 1 分！", ephemeral=True)
        return
    if amount > 60:
        await ctx.send(f"一次最多偷 60 分！", ephemeral=True)
        return
    try:
        msg = await ctx.send("准备偷窃中...")
        steal = Steal(msg.id, ctx.author, target, amount)
    except MultipleStealError:
        await msg.delete()
        await ctx.send(content="你已经在偷窃了，同时只可以偷一个人", ephemeral=True)
        return

    await msg.edit(content=steal.content(), view=steal.view())

@bot.command()
async def clearsteals(ctx):
    """清除所有闲置的偷窃"""
    delete_count, left_count = Steal.clear()
    await ctx.send(f"清除完毕，清理了{delete_count}个闲置的偷窃，还剩{left_count}个偷窃正在进行中")
