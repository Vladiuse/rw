from django.shortcuts import render, reverse, redirect, get_object_or_404
from .containers import ClientReader
from .forms import ClientContainer, ClientDocFileForm
from .models import ClientsReport, ClientContainerRow, WordDoc, ClientUser, FaceProxy
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from datetime import datetime
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from common import utils as common_utils
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def index(requets):
    return render(requets, 'containers/main.html')


@login_required
def people_count(requests):
    if requests.method != 'POST':
        return render(requests, 'containers/people_count.html')
    else:
        text = requests.POST['text']
        reader = ClientReader(text)
        reader.process()
        content = {
            'reader': reader,
            'text': text,
        }
        return render(requests, 'containers/clients/people_count.html', content)


@login_required
def clients_documents(request):
    if request.user.groups.filter(name='Админы').exists():
        clients_docs = ClientsReport.get_admin_reports()
    else:
        client_user = ClientUser.objects.get(user=request.user)
        clients_docs = ClientsReport.get_client_reports(client_user)
    content = {
        'clients_docs': clients_docs
    }
    return render(request, 'containers/clients/clients.html', content)


@login_required
def clients_document(request, document_id):
    if not (request.user.groups.filter(name='Админы').exists() or request.user.is_superuser):
        return HttpResponseRedirect(
            reverse('containers:client_document', args=(document_id,)))
    client_doc = ClientsReport.objects.get(pk=document_id)
    rows = ClientContainerRow.objects.filter(document=client_doc).annotate(past=client_doc.document_date - F('date'))
    rows_no_area = [row for row in rows if row.area == 0]
    rows_cont_number_error = [row for row in rows if not row.container_number_correct()]
    rows_cont_past_30 = [row for row in rows if row.is_past_30()]
    if request.method == 'POST':
        form = ClientContainer(request.POST, request.FILES, instance=client_doc)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('containers:show_client', args=(document_id,)))
        else:
            form_show = True
    else:
        form = ClientContainer(instance=client_doc)
        form_show = False
    content = {
        'client_doc': client_doc,
        'rows': rows,
        'rows_no_area': rows_no_area,
        'rows_cont_number_error': rows_cont_number_error,
        'form': form,
        'form_show': form_show,
        'rows_cont_past_30': rows_cont_past_30,
        'client_container_text_form': ClientDocFileForm(prefix='client_container',
                                                        instance=client_doc.client_container_doc),
    }
    return render(request, 'containers/clients/client.html', content)


@login_required
def client_document(request, document_id):
    client_user = get_object_or_404(ClientUser, user=request.user)
    # client_user = ClientUser.objects.get(user=request.user)
    client_doc = ClientsReport.objects.get(pk=document_id)
    rows = ClientContainerRow.objects.filter(document=client_doc, client_name=client_user.client_filter).annotate(
        past=client_doc.document_date - F('date'))
    content = {
        'rows': rows,
        'client_user': client_user,
    }
    return render(request, 'containers/clients/one_client.html', content)

@require_POST
def add_hand_text_to_docs(request, document_id):
    """Добавить в документ текст руками"""
    clients = ClientsReport.objects.get(pk=document_id)
    client_container_text_form = ClientDocFileForm(
        request.POST,
        request.FILES,
        prefix='client_container',
        instance=clients.client_container_doc,
    )
    if client_container_text_form.is_valid():
        client_container_text_form.save()
        if client_container_text_form.has_changed():
            clients.find_n_save_rows()
    return HttpResponseRedirect(
        reverse('containers:show_client', args=(document_id,)))


class CreateClientView(View, LoginRequiredMixin):
    """Создать отчет по клиентам"""

    def get(self, request, *args, **kwargs):
        client_form = ClientContainer(prefix='client_form')
        client_container_file_form = ClientDocFileForm(prefix='client_container')
        content = {
            'client_form': client_form,
            'client_container_text_form': client_container_file_form,
        }
        return render(request, 'containers/clients/create.html', content)

    def post(self, request, *args, **kwargs):
        client_form = ClientContainer(request.POST, prefix='client_form')
        client_container_file_form = ClientDocFileForm(request.POST, request.FILES, prefix='client_container')
        if client_container_file_form.is_valid():
            client_container_file_form.save()
            client_form.instance.client_container_doc = client_container_file_form.instance
        if client_form.is_valid():
            client_form.save()
            return redirect('containers:clients')
        content = {
            'client_form': client_form,
            'client_container_text_form': client_container_file_form,
        }
        return render(request, 'containers/clients/create.html', content)

@require_GET
@login_required
def files_no_data_rows(request, file_id):
    file = WordDoc.objects.get(pk=file_id)
    text = file.get_no_data_rows()
    text = text.replace('\n', '<br>')
    return HttpResponse(text)

@require_POST
@login_required
def delete(request, document_id):
    doc = ClientsReport.objects.get(pk=document_id)
    doc.delete()
    return redirect('containers:clients')

@login_required
def print_document(request, client_container_id):
    row = ClientContainerRow.objects.get(pk=client_container_id)
    client_user = ClientUser.objects.get(user=request.user)
    faces = FaceProxy.objects.filter(client=client_user)
    for face in faces:
        face.attorney_dash = f'{face.attorney:_<22}'
        face.name_dash = f'{face.name:_<18}'
    content = {
        'row': row,
        'text': 'Some text',
        'client_user': client_user,
        'faces': faces,
        'today': datetime.today().date(),
        'month_text': common_utils.month_text(datetime.today().month),
    }
    return render(request, 'containers/print/document_3.html', content)

@login_required
def users(request):
    users = User.objects.all()
    content = {
        'users': users,
    }
    return render(request, 'containers/users.html', content)

@login_required
def change_user(request, user_id):
    if request.user.groups.filter(name='Админы').exists() or request.user.is_superuser:
        if request.user.is_authenticated:
            logout(request)
        user = User.objects.get(pk=user_id)
        login(request, user)
        return HttpResponseRedirect(
            reverse('containers:clients'))
    else:
        user_to_change = User.objects.get(pk=user_id)
        current_client_user = request.user.clientuser
        if user_to_change.clientuser not in current_client_user.available_clients.all():
            return HttpResponse('Вам не доступен этот клиент')
        logout(request)
        user = User.objects.get(pk=user_id)
        login(request, user)
        return HttpResponseRedirect(
            reverse('containers:clients'))


def test(request):
    return HttpResponse('test page')

