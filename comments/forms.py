from django import forms

from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = [
            'comment',
        ]
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'id': 'comment-text',
                    'required': True,
                    'placeholder': 'Comment here'
                }
            ),
        }
