from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'pub_date', 'location', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
