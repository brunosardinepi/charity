from django import template


register = template.Library()

@register.simple_tag
def user_admin_status(user, type, obj):
    if type == "page":
        if user.userprofile in obj.admins.all():
            return "owner"
        elif user.userprofile in obj.managers.all():
            return "manager"
        else:
            return ""
    elif type == "campaign":
        if user.userprofile in obj.campaign_admins.all():
            return "owner"
        elif user.userprofile in obj.campaign_managers.all():
            return "manager"
        else:
            return ""
    else:
        return ""
