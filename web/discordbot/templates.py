import datetime

import discord
from discord.ext import commands

from .bot import bot
from .firebase_proxy import fb_get, fb_set, fb_template_get, fb_template_set, fb_template_getall


_template_keys = (
    "进入语音频道", "离开语音频道", "显示角色", "没有角色"
)

_templates = {
    "默认": {
        "price": 1,
        "进入语音频道": "欢迎 {member}（{timezone}）进入语音频道 {channel} ",
        "显示角色": "{member} 的角色有：{characters}",
        "没有角色": "没有找到属于 {member} 的角色",
    }
}


def _load_template(name):
    if name not in _templates:
        _templates[name] = fb_template_get(name)
    template = _templates[name] 

    if template is None:
        template = _templates[name] = {}
    return template


def _load_all_templates():
    global _templates
    templates = fb_template_getall()
    _templates = {
        "默认": _templates["默认"]
    }
    for name, template in templates.items():
        _templates[name] = template


def get_template(name, key):
    template = _load_template(name)
    return template.get(key, _templates["默认"].get(key))
    

def set_template(name, key, val):
    template = _load_template(name)
    template[key] = val
    fb_template_set(name, key, val)


def show_template(name):
    template = _load_template(name)
    ret = f"{name}: {template['price']}\n"
    ret += "\n".join(
        f"    {key}: {template[key]}" for key in _template_keys if key in template
    )
    return ret


def get_member_template(member, key):
    template_name = fb_get(member, "template")
    if not template_name:
        template_name = "默认"

    if template_name != "默认":
        template_expire_time = fb_get(member, "template_expire_time")
        if template_expire_time and template_expire_time < discord.utils.utcnow().timestamp():
            template_name = "默认"
            fb_set(member, "template", template_name)
            fb_set(member, "template_expire_time", None)

    return get_template(template_name, key)


@bot.command()
@commands.has_permissions(administrator=True)
async def settemplate(ctx, name, key, val):
    """设置模板"""
    if key == "price":
        val = int(val)
    set_template(name, key, val)
    await ctx.send(f"设置{name}的{key}为{val}", ephemeral=True)


@bot.hybrid_command()
async def buytemplate(ctx, name: str):
    """购买一个模板"""
    template = _load_template(name)
    if not template:
        await ctx.send(f'没有找到模板"{name}"', ephemeral=True)
        return

    price = get_template(name, "price")
    if not price:
        await ctx.send(f'没有找到模板"{name}"的价格', ephemeral=True)
        return

    credit = fb_get(ctx.author, "credit")

    if not credit or credit < price:
        await ctx.send(f'你的分数不足，购买模板"{name}"需要{price}信用点，你只有{credit}', ephemeral=True)
        return

    expire_time = discord.utils.utcnow() + datetime.timedelta(days=7)
    fb_set(ctx.author, "credit", credit - price)
    fb_set(ctx.author, "template", name)
    if name != "默认":
        fb_set(ctx.author, "template_expire_time", int(expire_time.timestamp()))
        await ctx.send(f"购买了模板{name}，过期时间为{expire_time.strftime('%Y-%m-%d %H:%M:%S')}", ephemeral=True)
    else:
        fb_set(ctx.author, "template_expire_time", None)
        await ctx.send(f"恢复了默认模板", ephemeral=True)


@bot.hybrid_command()
async def gifttemplate(ctx, member: discord.Member, name: str):
    """购买一个模板"""
    if name == "默认":
        await ctx.send(f"不能赠送默认模板", ephemeral=True)
        return

    template = _load_template(name)
    if not template:
        await ctx.send(f'没有找到模板"{name}"', ephemeral=True)
        return

    price = get_template(name, "price")
    if not price:
        await ctx.send(f'没有找到模板"{name}"的价格', ephemeral=True)
        return

    credit = fb_get(ctx.author, "credit")

    if not credit or credit < price:
        await ctx.send(f'你的分数不足，购买模板"{name}"需要{price}信用点，你只有{credit}', ephemeral=True)
        return

    expire_time = discord.utils.utcnow() + datetime.timedelta(days=7)
    fb_set(ctx.author, "credit", credit - price)
    fb_set(member, "template", name)
    fb_set(member, "template_expire_time", int(expire_time.timestamp()))
    await ctx.send(f"为{member.mention}购买了模板{name}，过期时间为{expire_time.strftime('%Y-%m-%d %H:%M:%S')}", ephemeral=True)


@bot.hybrid_command()
async def showtemplates(ctx):
    """显示所有模板"""
    _load_all_templates()
    ret = "\n\n".join(
        f"{show_template(name)}" for name in _templates.keys()
    )
    await ctx.send(ret)


@bot.hybrid_command()
async def mytemplate(ctx):
    """显示我的模板"""
    template = fb_get(ctx.author, "template")
    if not template:
        template = "默认"
    template_expire_time = fb_get(ctx.author, "template_expire_time")
    expire_time_str = f"，过期时间为{datetime.datetime.fromtimestamp(template_expire_time).strftime('%Y-%m-%d %H:%M:%S')}" if template_expire_time else ""
    await ctx.send(f'你的模板是"{template}"{expire_time_str}', ephemeral=True)
