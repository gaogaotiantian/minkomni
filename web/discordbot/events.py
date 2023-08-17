import discord

from .bot import bot
from .firebase_proxy import fb_get, fb_set
from .templates import get_member_template

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


@bot.event
async def on_command_error(ctx, error):
    print(error)


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        # 进入语音频道
        timezone = fb_get(member, "timezone") or "未知"
        ret = get_member_template(member, "进入语音频道").format(member=member.mention, timezone=timezone, channel=after.channel.mention) + '\n'
        characters = fb_get(member, "characters")
        if characters:
            ret += get_member_template(member, "显示角色").format(member=member.mention, characters=", ".join(characters))
        else:
            ret += get_member_template(member, "没有角色").format(member=member.mention)

        fb_set(member, "last_voice_channel_entry_time", int(discord.utils.utcnow().timestamp()))
        
        await member.guild.system_channel.send(ret)

    elif before.channel and not after.channel:
        # 离开语音频道
        last_voice_channel_entry_time = fb_get(member, "last_voice_channel_entry_time")
        characters = fb_get(member, "characters")
        template = get_member_template(member, "离开语音频道")
        if template:
            await member.guild.system_channel.send(template.format(member=member.mention, channel=before.channel.mention))

        if last_voice_channel_entry_time and characters:
            now = discord.utils.utcnow().timestamp()
            credit = fb_get(member, "credit")
            if credit is None:
                # 登录送50分
                credit = 50
            credit += int((now - last_voice_channel_entry_time) // 60)
            fb_set(member, "credit", credit)
