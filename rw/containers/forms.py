from django import forms
from .models import ClientsReport, WordDoc, ClientDocFile, AreaDocFile
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import DateInput
from django.core.files.base import ContentFile


class ClientContainer(forms.ModelForm):
    template_name = "containers/clients/client_form.html"

    # form_template_name = "vagons/base1.html"
    # document_date = forms.DateField(label='Дата документа', required=False, widget=AdminDateWidget)
    class Meta:
        model = ClientsReport
        # fields = '__all__'
        exclude = ['client_container_doc', 'area_doc']
        widgets = {
            # 'document_date': AdminDateWidget,
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 2}),
            'document_date': DateInput(attrs={'type': 'date'})
        }


class WordDocForm(forms.ModelForm):
    class Meta:
        model = WordDoc
        fields = ['word_doc_file']




class ClientDocForm(forms.ModelForm):
    class Meta:
        model = ClientDocFile
        fields = ['word_doc_file']

class AreaDocForm(forms.ModelForm):
    class Meta:
        model = AreaDocFile
        fields = ['word_doc_file']


class WordDocTextForm(WordDocForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}), required=False)
    def __init__(self, *args, **kwargs):
        super(WordDocTextForm, self).__init__(*args, **kwargs)
        self.fields['word_doc_file'].required = False

    def save(self, commit=True):
        instance = super(WordDocTextForm, self).save(commit=False)
        if 'word_doc_file' in self.changed_data:
            instance.read_word_doc()
        if self.cleaned_data['text']:
            instance.add_hand_text(self.cleaned_data['text'])
        if commit:
            instance.save()
        return instance


class ClientTextForm(ClientDocForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}), required=False)
    def __init__(self, *args, **kwargs):
        super(ClientDocForm, self).__init__(*args, **kwargs)
        self.fields['word_doc_file'].required = False

    def save(self, commit=True):
        instance = super(ClientDocForm, self).save(commit=False)
        if 'word_doc_file' in self.changed_data:
            instance.read_word_doc()
        if self.cleaned_data['text']:
            instance.add_hand_text(self.cleaned_data['text'])
        if commit:
            instance.save()
        return instance

class AreaTextForm(AreaDocForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}), required=False)
    def __init__(self, *args, **kwargs):
        super(AreaDocForm, self).__init__(*args, **kwargs)
        self.fields['word_doc_file'].required = False

    def save(self, commit=True):
        instance = super(AreaDocForm, self).save(commit=False)
        if 'word_doc_file' in self.changed_data:
            instance.read_word_doc()
        if self.cleaned_data['text']:
            instance.add_hand_text(self.cleaned_data['text'])
        if commit:
            instance.save()
        return instance
