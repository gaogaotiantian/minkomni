import datetime
import random

import discord

from ..firebase_proxy import fb_get, fb_set


_slots: dict[int, "Slots"] = {}

emojis = {
    0: ":apple:",
    1: ":banana:",
    2: ":cherries:",
    3: ":grapes:",
    4: ":lemon:",
    5: ":pineapple:",
    6: ":pear:",
    7: ":watermelon:"
}


class SlotsView(discord.ui.View):
    def __init__(self):
        # Timeout in 14 days
        self.role = None
        super().__init__(timeout=14*24*60*60)

    @discord.ui.button(label='摇一摇', style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        slots = _slots.get(interaction.message.id, None)
        if slots is None:
            await interaction.response.edit_message(content="摇摇水果机已经失效", view=None)
            return

        if slots.roll(interaction.user):
            await interaction.response.edit_message(content=slots.content())
        else:
            await interaction.response.send_message("你的余额不足", ephemeral=True)

    @discord.ui.button(label='删除', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        slots = _slots.get(interaction.message.id, None)
        if slots is None:
            await interaction.response.edit_message(content="摇摇水果机已经失效", view=None)
            return
        if interaction.user.guild_permissions.administrator:
            slots.delete()
            await interaction.message.delete()
        else:
            await interaction.response.send_message("你没有权限删除", ephemeral=True)


class Slots:
    def __new__(cls, id: int, bet: int):
        if id not in _slots:
            _slots[id] = super().__new__(cls)
        return _slots[id]

    def __init__(self, id: int, bet: int) -> None:
        self.id = id
        self.bet = bet
        self.results = {}
        self.last_active = discord.utils.utcnow()
        self.clear()

    def roll(self, member: discord.Member):
        self.last_active = discord.utils.utcnow()

        member_credit = fb_get(member, "credit") or 0

        if member_credit < self.bet:
            return False

        result = [random.randint(0, 7) for _ in range(5)]        
        credit = self.calculate_credit(result)

        if member.id in self.results:
            total_credit = credit + self.results[member.id]["total_credit"]
        else:
            total_credit = credit

        self.results[member.id] = {
            "result": result,
            "last_credit": credit,
            "total_credit": total_credit
        }

        self.update_credit(member, credit)

        return True

    def calculate_credit(self, result: list):
        rate = {
            (5,): 300,
            (4, 1): 20,
            (3, 2): 10,
            (3, 1, 1): 3,
            (2, 2, 1): 1,
            (2, 1, 1, 1): -1,
            (1, 1, 1, 1, 1): -2
        }
        cnts = tuple(sorted((result.count(i) for i in set(result)), reverse=True))
        return rate[cnts] * self.bet

    def update_credit(self, member: discord.Member, credit: int):
        original = fb_get(member, "credit")
        fb_set(member, "credit", original + credit)

    def content(self):
        ret = f"{''.join(emojis[i] for i in range(4))} 摇摇水果机 {''.join(emojis[i] for i in range(4, 8))} （基础分{self.bet}分）\n"
        ret += "====================================================================\n"
        ret += "游戏规则：\n"
        ret += "1. 每次摇摇水果机可能得到积分，也可能失去积分\n"
        ret += "2. 摇摇水果机的结果是5个水果，一共有8种水果\n"
        ret += "3. 摇摇水果机的结果会根据相同水果的数量来计算积分\n"
        ret += f"  - {emojis[0]*5} - :white_check_mark::three::zero::zero: 倍基础分\n"
        ret += f"  - {emojis[0]*4 + emojis[1]} - :white_check_mark::two::zero: 倍基础分\n"
        ret += f"  - {emojis[0]*3 + emojis[1]*2} - :white_check_mark::one::zero: 倍基础分\n"
        ret += f"  - {emojis[0]*3 + emojis[1] + emojis[2]} - :white_check_mark::three: 倍基础分\n"
        ret += f"  - {emojis[0]*2 + emojis[1]*2 + emojis[2]} - :white_check_mark::one: 倍基础分\n"
        ret += f"  - {emojis[0]*2 + emojis[1] + emojis[2] + emojis[3]} - :no_entry::one: 倍基础分\n"
        ret += f"  - {emojis[0] + emojis[1] + emojis[2] + emojis[3] + emojis[4]} - :no_entry::two: 倍基础分\n"
        ret += "====================================================================\n"
        for id, data in self.results.items():
            ret += f"<@{id}>: 上次结果{self.format_result(data['result'])}，获得{data['last_credit']}分，本游戏总积分{data['total_credit']}分\n"
        return ret

    def format_result(self, result: list):
        return "".join(emojis[i] for i in result)

    def view(self):
        return SlotsView()

    def delete(self):
        del _slots[self.id]

    @staticmethod
    def clear():
        delete_slots = []
        for _, slots in _slots.items():
            if discord.utils.utcnow() - slots.last_active > datetime.timedelta(days=1):
                delete_slots.append(slots)
        for slots in delete_slots:
            slots.delete()
        return len(delete_slots), len(_slots)
