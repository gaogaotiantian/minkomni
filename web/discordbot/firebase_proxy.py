import discord
from firebase_admin import db

def fb_get(member: discord.Member, attribute: str):
    ref = db.reference(f"/jx3/users/{member.id}")
    data = ref.get()

    if data and data.get(attribute):
        return data.get(attribute)
    else:
        return None

def fb_set(member: discord.Member, attribute: str, val):
    ref = db.reference(f"/jx3/users/{member.id}")
    ref.update({
        attribute: val
    })
