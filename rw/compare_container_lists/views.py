from django.shortcuts import render
from django.http import HttpResponse
from .forms import CompareTwoFileForm


def index(request):
    form = CompareTwoFileForm()
    if request.method == 'POST':
        form = CompareTwoFileForm(request.POST)
    content = {
        'form': form,
    }
    return render(request, 'compare_container_lists/compare_files_form.html', content)


def compare_containers(request):
    content = {
        'compare_type_name': 'Сверка номеров <br>вагонов',
        'default_file_name_1': 'Файл с вагонами №1',
        'default_file_name_2': 'Файл с вагонами №2',
    }

def compare_vagons(request):
    content = {
        'compare_type_name': 'Сверка списков <br>номеров контейнеров',
        'default_file_name_1': 'Файл с контейнерами №1',
        'default_file_name_2': 'Файл с контейнерами №2',
    }

