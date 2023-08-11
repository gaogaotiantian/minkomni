import aiohttp
import asyncio
import datetime

from .bot import bot


class Checker:
    def __init__(self):
        self.task = None
        self.msg = None

    async def start(self, msg):
        if self.task is not None and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.task = asyncio.create_task(self.check())
        if self.msg:
            await self.msg.delete()
        self.msg = msg
    
    async def check(self):
        while True:
            try:
                status = await self.do_check()
            except Exception:
                await self.msg.edit(content="查询出错")
                break

            if status is None:
                await self.msg.edit(content="查询出错")
                break

            if status:
                await self.msg.edit(content="服务器已经开启")
                self.task = None
                self.msg = None
                break
            else:
                t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
                await self.msg.edit(content=f'服务器维护中，上次查询时间：北京时间 {t.strftime("%Y-%m-%d %H:%M:%S")}')

            await asyncio.sleep(180)

    async def do_check(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v7.jx3api.com/data/server/check',
                                   params={'server': '梦江南'}) as response:
                if response.status != 200:
                    return None
                data = await response.json(content_type=None)

                if data['code'] != 200 or 'data' not in data:
                    return None
                if data['data']['status'] == 1:
                    return True
                return False

_checker = Checker()


@bot.hybrid_command()
async def monitorserver(ctx):
    """监控服务器状态"""
    msg = await ctx.send("正在查询服务器状态")
    await _checker.start(msg)
