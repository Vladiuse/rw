from django.shortcuts import render, reverse, redirect
from .containers import ContainerReader, ClientReader
from .forms import ClientContainer, ClientDocFileForm
from .models import ClientsReport, ClientContainerRow, WordDoc, ClientUser, FaceProxy
from django.db.models import F, Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required


def index(requet):
    if requet.method == 'POST':
        file_name_1 = requet.POST['file_name_1']
        file_name_2 = requet.POST['file_name_2']
        file_text_1 = requet.POST['file_text_1']
        file_text_2 = requet.POST['file_text_2']
        if file_text_1 == file_text_2:
            error_text = f'Текст файла {file_name_1} и {file_name_2} одинаковы!'
            return render(requet, 'containers/index.html', {'error_text': error_text})
        reader = ContainerReader(file_text_1, file_text_2)
        content = {

            'file_name_1': file_name_1,
            'file_name_2': file_name_2,
            'reader': reader
        }
        return render(requet, 'containers/new_result.html', content)
    else:
        return render(requet, 'containers/index.html')


def result(request):
    return render(request, 'containers/new_result.html')

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
        clients_docs = ClientsReport.objects.prefetch_related('clients').\
            annotate(container_count=Count('row')).order_by('-document_date')
    else:
        client_user = ClientUser.objects.get(user=request.user)
        clients_docs = client_user.reports\
            .annotate(container_count=Count(
            'row',Q(row__client_name=client_user.client_filter)
        )).order_by('-document_date')
    content = {
        'clients_docs': clients_docs
    }
    return render(request, 'containers/clients/clients.html', content)

@login_required
def clients_document(request, document_id):
    if not request.user.groups.filter(name='Админы').exists():
        return HttpResponseRedirect(
            reverse('containers:client_document', args=(document_id,)))
    client_doc = ClientsReport.objects.get(pk=document_id)
    rows = ClientContainerRow.objects.filter(document=client_doc).annotate(past=client_doc.document_date - F('date'))
    rows_no_area = [row for row in rows if row.area == 0]
    if request.method == 'POST':
        form = ClientContainer(request.POST, request.FILES,instance=client_doc)
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
        'form': form,
        'form_show': form_show,
        'client_container_text_form': ClientDocFileForm(prefix='client_container',instance=client_doc.client_container_doc),
    }
    return render(request, 'containers/clients/client.html', content)

@login_required
def client_document(request, document_id):
    client_user = ClientUser.objects.get(user=request.user)
    client_doc = ClientsReport.objects.get(pk=document_id)
    rows = ClientContainerRow.objects.filter(document=client_doc, client_name=client_user.client_filter).annotate(past=client_doc.document_date - F('date'))
    content = {
        'rows': rows,
        'client_user':client_user,
    }
    return render(request, 'containers/clients/one_client.html', content)


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




@login_required
def create_client(request):
    """Создать отчет по клиентам"""
    if request.method == 'POST':
        client_form = ClientContainer(request.POST, prefix='client_form')
        client_container_file_form = ClientDocFileForm(request.POST, request.FILES,prefix='client_container')
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
    else:
        client_form = ClientContainer(prefix='client_form')
        client_container_file_form = ClientDocFileForm(prefix='client_container')
        content = {
            'client_form': client_form,
            'client_container_text_form': client_container_file_form,
        }
        return render(request, 'containers/clients/create.html', content)

def files_no_data_rows(request, file_id):
    file = WordDoc.objects.get(pk=file_id)
    text = file.get_no_data_rows()
    text = text.replace('\n', '<br>')
    return HttpResponse(text)

@login_required
def delete(request, document_id):
    doc = ClientsReport.objects.get(pk=document_id)
    doc.delete()
    return redirect('containers:clients')


def print_document(request, client_container_id):
    row = ClientContainerRow.objects.get(pk=client_container_id)
    faces = FaceProxy.objects.all()
    client_user = ClientUser.objects.get(user=request.user)
    for face in faces:
        face.name_dash = f'{face.name:_<34}'
        face.attorney_dash = f'{face.attorney:_<23}'
    content = {
        'row': row,
        'text': 'Some text',
        'faces': faces,
        'client_user': client_user,
    }
    return render(request, 'containers/print/document.html', content)


def test(request):

    content = {
        'client_container_form': ClientDocFileForm(),
    }
    return render(request, 'containers/test.html', content)


