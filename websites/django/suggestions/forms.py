from .models import Suggestions
from django.forms import ModelForm, TextInput, DateTimeInput, Textarea


class SuggestionsForm(ModelForm):
    class Meta:
        model = Suggestions
        fields = ['title', 'text', 'date']

        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название'
            }),
            "text": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Текст'
            }),
            "date": DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дата публикации'
            })
        }