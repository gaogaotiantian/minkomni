import aiohttp

import discord

from .bot import bot


@bot.hybrid_command()
async def daily(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.jx3api.com/view/active/current',
                               params={'server': '梦江南', 'cache': 1, 'robot': '双梦的时差党们'}) as response:
            if response.status != 200:
                await ctx.send(f'服务器挂了！')
                return
            data = await response.json(content_type=None)
            url = data['data']['url']

    await ctx.send(embed=discord.Embed(type='image').set_image(url=url))
