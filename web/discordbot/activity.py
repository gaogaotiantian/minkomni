import discord
from .firebase_proxy import fb_activity_get, fb_activity_set

from .bot import bot


class Activity:
    def __init__(self,
                 id: int,
                 author: int,
                 guild: int,
                 title: str,
                 description: str,
                 create_time: int,
                 participants: list = []):
        self.id = id
        self.author = author
        self.guild = guild
        self.title = title
        self.description = description
        self.create_time = create_time
        self.participants = participants

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "guild": self.guild,
            "title": self.title,
            "description": self.description,
            "create_time": self.create_time,
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
            create_time=dict.get("create_time", 0),
            participants=dict.get("participants", {}))

    @staticmethod
    def from_id(id: int):
        dict = fb_activity_get(id)
        if not dict:
            return None
        # Firebase stores key as string, convert it back to int
        dict["participants"] = {int(k): v for k, v in dict.get("participants", {}).items()}
        return Activity.from_dict(dict)

    def add_participant(self, member: int, role: str):
        if member not in self.participants:
            self.participants[member] = {
                "role": role
            }
            return True
        return False

    def remove_participant(self, member: int):
        if member in self.participants:
            self.participants.pop(member)
            return True
        return False

    def view(self):
        guild = bot.get_guild(self.guild)

        ret = f'活动：{self.title}（{self.id}）\n' if self.id is not None else f'活动：{self.title}\n'
        ret += f'发起人：{guild.get_member(self.author).mention}\n\n'
        ret += f'{self.description}\n\n'
        plist = []
        for p, data in self.participants.items():
            plist.append(f'{guild.get_member(p).mention}（{data["role"]}）')
        ret += f'报名者（{len(plist)}）：{", ".join(plist)}\n'

        return ret

    def save(self):
        if self.id is not None:
            fb_activity_set(self.id, self.to_dict())

    def delete(self):
        if self.id is not None:
            fb_activity_set(self.id, {})


class ActivityMsgView(discord.ui.View):
    def __init__(self):
        # Timeout in 14 days
        self.role = None
        super().__init__(timeout=14*24*60*60)

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder='直接选择定位即可报名',
        max_values=3,
        min_values=1,
        custom_id="activity_msg_view_role",
        options=[
            discord.SelectOption(label='T', value='T', emoji="🛡️"),
            discord.SelectOption(label='N', value='N', emoji="⚕️"),
            discord.SelectOption(label='D', value='D', emoji="⚔️"),
        ]
    )
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        activity = Activity.from_id(interaction.message.id)
        if activity:
            role = " | ".join(sorted(select.values, reverse=True))
            if activity.add_participant(interaction.user.id, role):
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
        create_time=ctx.message.created_at.timestamp(),
        participants={}
    )
    msg = await ctx.send(activity.view(), view=ActivityMsgView())
    activity.id = msg.id
    # Update the id in the message
    await msg.edit(content=activity.view())
    activity.save()
    await ctx.message.delete()


@bot.hybrid_command()
async def repostactivity(ctx, id: int):
    """转发一个存在的活动"""
    activity = Activity.from_id(id)
    if activity:
        msg = await ctx.send(activity.view(), view=ActivityMsgView())
        # Delete the original activity
        activity.delete()
        # Update the id in the message
        activity.id = msg.id
        await msg.edit(content=activity.view())
        activity.save()
        await ctx.message.delete()
    else:
        await ctx.send(f"没有找到id为{id}的活动", delete_after=5)
