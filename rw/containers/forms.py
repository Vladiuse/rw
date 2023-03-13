from django import forms
from .models import ClientDoc, WordDoc
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import DateInput

class ClientDocForm(forms.ModelForm):
    template_name = "containers/clients/client_form.html"
    # form_template_name = "vagons/base1.html"
    # document_date = forms.DateField(label='Дата документа', required=False, widget=AdminDateWidget)
    class Meta:
        model = ClientDoc
        fields = '__all__'
        widgets = {
            # 'document_date': AdminDateWidget,
            'description' : forms.Textarea(attrs={'cols': 40, 'rows': 2}),
            'document_date': DateInput(attrs={'type': 'date'})
        }

class WordDocForm(forms.ModelForm):
    class Meta:
        model = WordDoc
        fields = ['doc_file', 'text_file']