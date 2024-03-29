import discord
from firebase_admin import db


def fb_get_users():
    ref = db.reference("/jx3/users")
    return ref.get()


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


def fb_template_get(template_id: str):
    ref = db.reference(f"/jx3/templates/{template_id}")
    ret = ref.get()
    return ret

def fb_template_set(template_id: str, key: str, val):
    ref = db.reference(f"/jx3/templates/{template_id}")
    ref.update({
        key: val
    })

def fb_template_getall():
    ref = db.reference(f"/jx3/templates")
    ret = ref.get()
    if ret is None:
        ret = {}
    return ret
