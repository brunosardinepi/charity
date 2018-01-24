from django import template
from django.contrib.contenttypes.models import ContentType

from userprofile.models import UserImage


register = template.Library()

@register.filter
def content_type_pk(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj).pk

@register.filter
def content_type(obj):
    if not obj:
        return False
    return str(ContentType.objects.get_for_model(obj))

@register.filter
def img_class(img, size):
    height = img.height
    width = img.width

    if height < (width - 60):
        html = "circular-landscape"
    elif height > (width + 60):
        html = "circular-portrait"
    else:
        html = "circular-square"

    if size == "small":
        html += "-sm"

    return html

@register.simple_tag
def get_img_from_pk(pk, type):
    if type == "user":
        return UserImage.objects.get(pk=pk)

@register.filter
def convert_to_pct(obj):
    if not obj:
        obj = 0
    return "{}%".format(int(obj * 100))
