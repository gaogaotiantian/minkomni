from .bot import bot
from .firebase_proxy import fb_get, fb_set

@bot.hybrid_command()
async def querycredit(ctx):
    """查询自己的分数"""
    credit = fb_get(ctx.author, "credit")
    if credit is None:
        credit = 50
        fb_set(ctx.author, "credit", credit)

    await ctx.send(f'你的分数是：{credit}')
