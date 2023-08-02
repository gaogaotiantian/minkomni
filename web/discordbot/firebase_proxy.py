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


def fb_activity_clear():
    ref = db.reference(f"/jx3/activities")
    ref.delete()


def fb_activity_set(activity_id: str, val):
    ref = db.reference(f"/jx3/activities/{activity_id}")
    ref.set(val)


def fb_activity_get(activity_id: str):
    ref = db.reference(f"/jx3/activities/{activity_id}")
    ret = ref.get()
    return ret
