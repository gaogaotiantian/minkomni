import aiohttp
import asyncio
import datetime

import discord

from .bot import bot


class Checker:
    def __init__(self):
        self.task = None
        self._channel_id = None
        self._msg_id = None

    # We need to get the message from id every time because the webhook expires
    async def get_msg(self):
        if self._channel_id and self._msg_id:
            channel = bot.get_channel(self._channel_id)
            if channel:
                return await channel.fetch_message(self._msg_id)
        return None

    def set_msg(self, msg):
        if msg is None:
            self._channel_id = None
            self._msg_id = None
        else:
            self._channel_id = msg.channel.id
            self._msg_id = msg.id

    async def start(self, msg):
        if self.task is not None and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        cur_msg = await self.get_msg()
        if cur_msg:
            await cur_msg.delete()
        self.set_msg(msg)
        self.task = asyncio.create_task(self.check())
    
    async def check(self):
        try:
            in_service = False
            while True:
                msg = await self.get_msg()
                status = await self.do_check()

                if status is None:
                    await msg.edit(content="查询出错")
                    break

                if status:
                    await msg.edit(content="服务器已经开启")
                    if in_service:
                        await bot.get_channel(msg.channel.id).send("@here 小伙伴们，梦江南已经开服啦！可以上线啦！")
                    break
                else:
                    in_service = True
                    t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
                    await msg.edit(content=f'服务器维护中，上次查询时间：北京时间 {t.strftime("%Y-%m-%d %H:%M:%S")}')

                await asyncio.sleep(120)
        except Exception:
            await msg.edit(content="查询出错")
        finally:
            self.task = None
            self.set_msg(None)

    async def do_check(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.jx3api.com/data/server/check',
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
