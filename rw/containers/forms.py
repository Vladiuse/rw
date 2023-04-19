from django import forms
from .models import ClientsReport, WordDoc, ClientDocFile
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError


class ClientContainer(forms.ModelForm):
    template_name = "containers/clients/client_form.html"

    class Meta:
        model = ClientsReport
        exclude = ['client_container_doc', 'area_doc']
        widgets = {
            # 'document_date': AdminDateWidget,
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 2}),
            'document_date': DateInput(attrs={'type': 'date'})
        }


class WordDocForm(forms.ModelForm):
    hand_text = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}), required=False)

    class Meta:
        model = WordDoc
        fields = ['word_doc_file']

    def clean(self):
        super().clean()
        if not any([self.cleaned_data['word_doc_file'], self.cleaned_data['hand_text']]):
            raise ValidationError(
                'File or Text must be added!'
            )

    def save(self, commit=True):
        instance = super(WordDocForm, self).save(commit=False)
        if commit:
            instance.save()
        if 'word_doc_file' in self.changed_data:
            print('IN CHANGE')
            instance.check_word_doc()
        if 'hand_text' in self.changed_data:
            instance.add_hand_text(self.cleaned_data['hand_text'])
        return instance




class ClientDocFileForm(WordDocForm):
    class Meta(WordDocForm.Meta):
        model = ClientDocFile
        fields = ['type', 'word_doc_file']



