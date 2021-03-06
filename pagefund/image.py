from django.conf import settings

from campaign.models import Campaign
from page.models import Page
from userprofile.models import UserProfile


def image_is_valid(request, form, model):
    if form.is_valid():
        image_raw = form.cleaned_data.get('image',False)
        if image_raw:
            image_type = image_raw.content_type.split('/')[0]
            if image_type in settings.UPLOAD_TYPES:
                if image_raw._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                    data = {'is_valid': 'f', 'redirect': "error_size"}
                else:
                    image = form.save(commit=False)
                    if type(model) is UserProfile:
                        image.user = model
                    elif type(model) is Page:
                        image.page = model
                        image.uploaded_by = request.user
                    elif type(model) is Campaign:
                        image.campaign = model
                        image.uploaded_by = request.user
                    image.save()
                    data = {
                        'is_valid': 't',
                        'name': image.image.name,
                        'pk': image.pk,
                        'url': image.image.url,
                        'type': model.__class__.__name__,
                    }
            else:
                 data = {'is_valid': 'f', 'redirect': "error_type"}
            return data

