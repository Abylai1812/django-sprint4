from django import forms

from .models import PostCreate,Comment

class PostForm(forms.ModelForm):

    class Meta:
        model = PostCreate
        fields = '__all__'

        widgets= {
            'pub_date':forms.DateInput(attrs={'type':'date'})
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)