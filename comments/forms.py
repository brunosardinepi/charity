from django import forms

from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = [
            'content',
        ]
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'id': 'comment-text',
                    'required': True,
                    'placeholder': 'Comment here'
                }
            )
        }
