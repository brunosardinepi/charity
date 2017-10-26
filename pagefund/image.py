from django.conf import settings

from campaign.models import Campaign
from page.models import Page
from userprofile.models import UserProfile


def image_is_valid(form, model):
    if form.is_valid():
        image_raw = form.cleaned_data.get('image',False)
        image_type = image_raw.content_type.split('/')[0]
        if image_type in settings.UPLOAD_TYPES:
            if image_raw._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                 data = {'is_valid': False, 'redirect': "error_size"}
            image = form.save(commit=False)
            if type(model) is UserProfile:
                image.user = model
            elif type(model) is Page:
                image.page = model
            elif type(model) is Campaign:
                image.campaign = model
            image.save()
            data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
        else:
             data = {'is_valid': False, 'redirect': "error_type"}
        return data

