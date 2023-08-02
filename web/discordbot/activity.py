import discord
from .firebase_proxy import fb_activity_get, fb_activity_set

from .bot import bot


class Activity:
    def __init__(self, id: int, author: int, guild: int, title: str, description: str, participants: list = []):
        self.id = id
        self.author = author
        self.guild = guild
        self.title = title
        self.description = description
        self.participants = participants

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "guild": self.guild,
            "title": self.title,
            "description": self.description,
            "participants": self.participants
        }

    @staticmethod
    def from_dict(dict):
        return Activity(
            id=dict["id"],
            author=dict["author"],
            guild=dict["guild"],
            title=dict["title"],
            description=dict["description"],
            participants=dict.get("participants", []))

    @staticmethod
    def from_id(id: int):
        dict = fb_activity_get(id)
        if not dict:
            return None
        return Activity.from_dict(dict)

    def add_participant(self, member: int):
        if member not in self.participants:
            self.participants.append(member)
            return True
        return False

    def remove_participant(self, member: int):
        if member in self.participants:
            self.participants.remove(member)
            return True
        return False

    def view(self):
        guild = bot.get_guild(self.guild)

        ret = f'活动：{self.title}\n'
        ret += f'发起人：{guild.get_member(self.author).mention}\n\n'
        ret += f'{self.description}\n\n'
        ret += f'报名者（{len(self.participants)}）：{", ".join([guild.get_member(p).mention for p in self.participants])}\n'

        return ret

    def save(self):
        if self.id is not None:
            fb_activity_set(self.id, self.to_dict())

    def delete(self):
        if self.id is not None:
            fb_activity_set(self.id, {})


class ActivityMsgView(discord.ui.View):
    @discord.ui.button(label='报名', style=discord.ButtonStyle.green)
    async def signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        activity = Activity.from_id(interaction.message.id)
        if activity:
            if activity.add_participant(interaction.user.id):
                activity.save()
                await interaction.response.edit_message(content=activity.view())
            else:
                await interaction.response.send_message("你已经报过名了", ephemeral=True)
        else:
            await interaction.response.send_message("活动已经不存在了", ephemeral=True)

    @discord.ui.button(label='取消报名', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        activity = Activity.from_id(interaction.message.id)
        if activity:
            if activity.remove_participant(interaction.user.id):
                activity.save()
                await interaction.response.edit_message(content=activity.view())
            else:
                await interaction.response.send_message("你还没有报名", ephemeral=True)
        else:
            await interaction.response.send_message("活动已经不存在了", ephemeral=True)

    @discord.ui.button(label='删除活动', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        activity = Activity.from_id(interaction.message.id)
        if activity:
            if activity.author == interaction.user.id or interaction.user.guild_permissions.administrator:
                activity.delete()
                await interaction.message.delete()
            else:
                await interaction.response.send_message("你没有权限删除这个活动", ephemeral=True)
        else:
            await interaction.response.send_message("活动已经不存在了", ephemeral=True)


@bot.hybrid_command()
async def addactivity(ctx, title: str, description: str):
    """发起一个新的活动"""
    activity = Activity(
        id=None,
        author=ctx.author.id,
        guild=ctx.guild.id,
        title=title,
        description=description,
        participants=[]
    )
    msg = await ctx.send(activity.view(), view=ActivityMsgView())
    activity.id = msg.id
    activity.save()
    await ctx.message.delete()
