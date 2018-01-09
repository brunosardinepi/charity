from django import forms

from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = [
            'comment',
            'content_type',
            'object_id',
        ]
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'id': 'comment-text',
                    'required': True,
                    'placeholder': 'Comment here'
                }
            ),
            'content_type': forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }
