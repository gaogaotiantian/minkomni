import aiohttp

from .bot import bot


def format_price_list(price_list):
    
    def format_price(price, display_max):
        price //= 100
        z = price // 1000000
        j = (price // 100) % 10000
        y = price % 100
        ret = ""
        if z:
            ret += f"{z:>3}z"
        if z or j:
            ret += f"{j:>5}j"
        ret += f"{y:>3}y"

        if display_max == "z":
            return f"{ret:>14}"
        elif display_max == "j":
            return f"{ret:>10}"
        else:
            return f"{ret:>4}"

    items = [d[0] for d in price_list]
    prices = [d[1] for d in price_list]

    max_len = max(len(item) for item in items)
    max_price = max(prices)
    display_max = "z" if max_price >= 100000000 else "j" if max_price >= 10000 else "y"

    return '```' + \
           '\n'.join(f'{item:<{max_len}}： {format_price(price, display_max)}' for item, price in price_list) + \
           '```'


@bot.hybrid_command()
async def queryprice(ctx, item: str):
    """查询物品价格"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://node.jx3box.com/item_merged/name/{item}',
                               headers={'accept': 'application/json'},
                               params={'per': 50}) as response:
            if response.status != 200:
                await ctx.send(f'服务器挂了！')
                return

            # jx3box api sends the wrong content type
            data = await response.json(content_type=None)
            if data['total'] == 0:
                await ctx.send(f'没有找到物品"{item}"')
                return

            items = {item['id']: item['Name'] for item in data['list']}
        
        async with session.get('https://next2.jx3box.com/api/item-price/list',
                               params={'itemIds': ','.join(items.keys()),
                                       'server': '梦江南'}) as response:
            if response.status != 200:
                await ctx.send(f'服务器挂了！')
                return

            price_list = []
            data = await response.json(content_type=None)
            if not data['data']:
                await ctx.send(f'没有找到和物品"{item}"有关的价格信息')
                return

            for item_id in data['data']:
                price = data['data'][item_id]['LowestPrice']
                price_list.append((items[item_id], price))

            await ctx.send(format_price_list(price_list))
