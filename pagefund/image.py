from django.conf import settings
from django.core.exceptions import ValidationError
from page import forms
from page import models

def image_upload(image_form):
    image = image_form.cleaned_data.get('icon',False)
    image_type = image.content_type.split('/')[0]
    if image_type in settings.UPLOAD_TYPES:
        if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
            msg = 'The file size limit is %s. Your file size is %s.' % (
                settings.MAX_IMAGE_UPLOAD_SIZE,
                image._size
            )
            raise ValidationError(msg)
