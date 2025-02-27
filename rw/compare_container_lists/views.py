from django.shortcuts import render
from .forms import CompareTwoFileForm
from django.views import View
from .types import reader_types
from django.contrib.auth.mixins import LoginRequiredMixin

class CompareListsView(LoginRequiredMixin, View):
    form_template = 'compare_container_lists/compare_files_form.html'
    result_template = 'compare_container_lists/compare_lists_result.html'

    def get(self, request, *args, **kwargs):
        form = CompareTwoFileForm()
        content = {
            'form': form,
        }
        return render(request, self.form_template, content)

    def post(self, request, *args, **kwargs):
        form = CompareTwoFileForm(request.POST)
        if form.is_valid():
            reader_class = reader_types[form.cleaned_data['type']]
            reader = reader_class(
                form.cleaned_data['file_text_1'],
                form.cleaned_data['file_text_2'],
            )
            content = {
                'reader': reader,
            }
            return render(request,self.result_template, content)
        content = {
            'form': form,
        }
        return render(request, self.form_template, content)
