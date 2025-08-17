from django import forms

from .models import PostCreate

class PostForm(forms.ModelForm):

    class Meta:
        model = PostCreate
        fields = '__all__'

        widgets= {
            'pub_date':forms.DateInput(attrs={'type':'date'})
        }