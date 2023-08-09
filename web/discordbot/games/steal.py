import datetime

import discord

from ..firebase_proxy import fb_get, fb_set


_steals: dict[int, "Steal"] = {}
_stealers = {}


class MultipleStealError(Exception):
    pass


class SlotsView(discord.ui.View):
    def __init__(self):
        # Timeout in 3 day
        self.role = None
        super().__init__(timeout=3*24*60*60)

    @discord.ui.button(label='收获', style=discord.ButtonStyle.primary)
    async def collect(self, interaction: discord.Interaction, button: discord.ui.Button):
        steal = _steals.get(interaction.message.id, None)
        if steal is None:
            await interaction.response.edit_message(content="本次偷窃已经失效", view=None)
            return
        
        if interaction.user != steal.stealer:
            await interaction.response.send_message("你不是偷窃者", ephemeral=True)
            return

        try:
            if steal.collect():
                await interaction.response.edit_message(content=steal.content(), view=None)
            else:
                await interaction.response.send_message(f"还有 {steal.minutes_left()} 分钟就能收分了，再等等", ephemeral=True)
        except Exception as e:
            print(e)

    @discord.ui.button(label='抓住！', style=discord.ButtonStyle.red)
    async def catch(self, interaction: discord.Interaction, button: discord.ui.Button):
        steal = _steals.get(interaction.message.id, None)
        if steal is None:
            await interaction.response.edit_message(content="本次偷窃已经失效", view=None)
            return
        
        if interaction.user != steal.target:
            await interaction.response.send_message("你不是被偷者", ephemeral=True)
            return

        if steal.catch():
            await interaction.response.edit_message(content=steal.content(), view=None)
        else:
            await interaction.response.send_message("很遗憾，分数已经被偷走了", ephemeral=True)


class Steal:
    def __new__(self, id: int, stealer: discord.Member, target: discord.Member, amount: int):
        if stealer.id in _stealers:
            raise MultipleStealError()
        if id not in _steals:
            _steals[id] = super().__new__(self)
            _stealers[stealer.id] = id
        return _steals[id]

    def __init__(self, id: int, stealer: discord.Member, target: discord.Member, amount: int):
        self.id = id
        self.stealer = stealer
        self.target = target
        self.amount = amount
        self.time_cost = amount * 2
        self.fail_punishment = max(1, int(self.amount // 10))
        self.success = None
        self.steal_time = discord.utils.utcnow()
        self.collect_time = discord.utils.utcnow() + datetime.timedelta(minutes=self.time_cost)
        self.clear()

    def collect(self):
        if discord.utils.utcnow() < self.collect_time:
            return False

        stealer_credit = fb_get(self.stealer, "credit") or 0
        stealer_credit += self.amount
        fb_set(self.stealer, "credit", stealer_credit)

        target_credit = fb_get(self.target, "credit") or 0
        target_credit -= self.amount
        fb_set(self.target, "credit", target_credit)

        self.success = True
        self.delete()
        return True

    def catch(self):
        if self.success:
            return False
        stealer_credit = fb_get(self.stealer, "credit") or 0
        stealer_credit -= self.fail_punishment
        fb_set(self.stealer, "credit", stealer_credit)
        self.success = False
        self.delete()
        return True

    def minutes_left(self):
        return (self.collect_time - discord.utils.utcnow()).seconds // 60

    def delete(self):
        del _steals[self.id]
        del _stealers[self.stealer.id]

    @staticmethod
    def clear():
        now = discord.utils.utcnow()
        delete_steals = []
        for steal in _steals.values():
            if now > steal.collect_time + datetime.timedelta(days=1):
                delete_steals.append(steal)
        for steal in delete_steals:
            steal.delete()
        return len(delete_steals), len(_steals)

    def content(self):
        if self.success is None:
            ret = f"{self.stealer.mention}正在偷窃{self.target.mention}的 {self.amount} 分，偷窃耗时 {self.time_cost} 分钟。\n"
            ret += "到时间后，偷窃者需要按“收获”按钮收获分数\n"
            ret += "在偷窃者按收获按钮之前，被偷窃者可以按“抓住！”按钮阻止偷窃，成功阻止偷窃将会惩罚偷窃者准备偷窃分数的 1/10（最少 1 分）\n"
            return ret
        elif self.success:
            return f"{self.stealer.mention}成功偷窃{self.target.mention}的 {self.amount} 分"
        else:
            return f"{self.stealer.mention}试图偷窃被{self.target.mention}抓住了，惩罚 {self.fail_punishment} 分"

    def view(self):
        return SlotsView()
