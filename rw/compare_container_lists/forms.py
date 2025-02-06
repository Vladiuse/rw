from django import forms
from django.core.validators import ValidationError
from .types import CONTAINERS, VAGONS


choices = [(CONTAINERS, 'Всерка контейнеров'), (VAGONS, 'Сверка вагонов')]
class CompareTwoFileForm(forms.Form):
    type = forms.ChoiceField(choices=choices, initial=CONTAINERS)
    file_name_1 = forms.CharField(required=True, initial='Файл #1')
    file_name_2 = forms.CharField(required=True, initial='Файл #2')
    file_text_1 = forms.CharField(required=True)
    file_text_2 = forms.CharField(required=True)


    def clean(self):
        cleaned_data = super().clean()
        file_name_1 = cleaned_data.get('file_name_1')
        file_name_2 = cleaned_data.get('file_name_2')

        if file_name_1 == file_name_2:
            raise ValidationError('Названия файлов должны быть разными!')
