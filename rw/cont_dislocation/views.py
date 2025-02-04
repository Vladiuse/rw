from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from containers.containers.containers_reader import Container
from django.db.models import Count
from containers.models import ClientsReport, ClientContainerRow
from django.views import View
from .utils import get_area_type

class ContainerDislocationView(View):
    template = 'cont_dislocation/container_dislocation.html'

    def _get_last_client_report(self):
        return ClientsReport.objects.annotate(container_count=Count('row')).filter(
            container_count__gt=0).latest('document_date', '-pk')

    def get(self, request, *args, **kwargs):
        if not (request.user.groups.filter(name='Админы').exists() or request.user.is_superuser):
            return HttpResponse('Недоступно')
        content = {
            'report': self._get_last_client_report(),
        }
        return render(request, self.template, content)

    def post(self, request, *args, **kwargs):
        if not (request.user.groups.filter(name='Админы').exists() or request.user.is_superuser):
            return HttpResponse('Недоступно')
        last_client_report = self._get_last_client_report()
        container = request.POST['container']
        send_number = request.POST['send_number']
        if not Container._is_number_correct(container):
            result = {
                'status': False,
                'msg': 'Некоректный номер контейнера (не правильная контрольная сумма)'
            }
            return JsonResponse(result)
        try:
            client_row = ClientContainerRow.objects.get(document=last_client_report, send_number=send_number,
                                                        container=container)
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
        except ClientContainerRow.DoesNotExist as error:
            result = {
                'status': False,
                'msg': 'Ошибка, проверьте внесенные данные',
                'error_str': str(error),
            }
        return JsonResponse(result, safe=True)

