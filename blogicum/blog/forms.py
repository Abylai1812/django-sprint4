from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


User = get_user_model()

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)

        widgets = {
            'pub_date': forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            )
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'E-mail',
        }