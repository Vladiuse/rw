from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from containers.containers.containers_reader import Container
from clients.models import Book, Container as ContainerModel
from django.views import View
from .utils import get_area_type


class ContainerDislocationView(LoginRequiredMixin, View):
    template = 'cont_dislocation/container_dislocation.html'

    def _get_last_uploading_book(self):
        return Book.objects.filter(type=Book.UNLOADING_BOOK).latest('book_date', 'pk')

    def get(self, request, *args, **kwargs):
        content = {
            'book': self._get_last_uploading_book(),
        }
        return render(request, self.template, content)

    def post(self, request, *args, **kwargs):
        last_uploading_book = self._get_last_uploading_book()
        print(last_uploading_book)
        container_number = request.POST['container']
        send_number = request.POST['send_number']
        print(request.POST)
        if not Container._is_number_correct(container_number):
            result = {
                'status': False,
                'msg': 'Некоректный номер контейнера (не правильная контрольная сумма)'
            }
            return JsonResponse(result)
        try:
            client_row = ContainerModel.objects.get(book=last_uploading_book, send_number=send_number,
                                                    number=container_number)
            if client_row.area:
                area_type = get_area_type(client_row.area)
                area_text = f'{client_row.area} участок ({area_type})'
            else:
                area_text = 'Участок не указан'
            result = {
                'status': True,
                'msg': 'Model found',
                'area_text': area_text,
                'area': client_row.area,
            }
        except ContainerModel.DoesNotExist as error:
            result = {
                'status': False,
                'msg': 'Ошибка, проверьте внесенные данные',
                'error_str': str(error),
            }
        return JsonResponse(result, safe=True)

