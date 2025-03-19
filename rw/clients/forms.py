from django import forms
from django.forms.widgets import DateInput, DateTimeInput
from django.core.files.base import ContentFile
from .models import Book
from .utils import get_name_for_book_file


class TextBookForm(forms.ModelForm):
    text = forms.CharField(initial='', required=True)
    class Meta:
        model = Book
        exclude = ('file',)
        widgets = {
            'book_date': DateInput(attrs={'type': 'date'})
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        file_content = ContentFile(self.cleaned_data['text'])
        file_name = get_name_for_book_file(date=instance.book_date, book_type=instance.type)
        instance.file.save(file_name, file_content, save=False)
        if commit:
            instance.save()
        return instance
