from django import template


register = template.Library()

@register.simple_tag
def user_admin_status(user, type, obj):
    if type == "page":
        if user.userprofile in obj.admins.all():
            return "Owner"
        elif user.userprofile in obj.managers.all():
            return "Manager"
        else:
            return "Subscribed"
    elif type == "campaign":
        if user.userprofile in obj.campaign_admins.all():
            return "Owner"
        elif user.userprofile in obj.campaign_managers.all():
            return "Manager"
        else:
            return "Subscribed"
    else:
        return ""
