from django import forms
from .models import ClientDoc, WordDoc, ClientDocFile, AreaDocFile
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import DateInput


class ClientContainer(forms.ModelForm):
    template_name = "containers/clients/client_form.html"

    # form_template_name = "vagons/base1.html"
    # document_date = forms.DateField(label='Дата документа', required=False, widget=AdminDateWidget)
    class Meta:
        model = ClientDoc
        # fields = '__all__'
        exclude = ['client_container_doc', 'area_doc']
        widgets = {
            # 'document_date': AdminDateWidget,
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 2}),
            'document_date': DateInput(attrs={'type': 'date'})
        }


class ClientDocForm(forms.ModelForm):
    class Meta:
        model = ClientDocFile
        fields = ['doc_file']

class AreaDocForm(forms.ModelForm):
    class Meta:
        model = AreaDocFile
        fields = ['doc_file']


class WordDocTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}))
