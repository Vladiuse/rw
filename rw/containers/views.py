from django.shortcuts import render, reverse, redirect
from .containers import ContainerReader, ClientReader
from .forms import ClientContainer, WordDocForm, ClientDocFileForm, AreaDocFileForm
from .models import ClientsReport, ClientContainerRow, WordDoc
from django.db.models import F
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

@login_required
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

@login_required
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
def clients(request):
    clients_docs = ClientsReport.objects.select_related('client_container_doc').select_related('area_doc').all()
    content = {
        'clients_docs': clients_docs
    }
    return render(request, 'containers/clients/clients.html', content)

@login_required
def client(request, document_id):
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
        'area_text_form': AreaDocFileForm(prefix='area',instance=client_doc.area_doc),
    }
    return render(request, 'containers/clients/client.html', content)



def add_hand_text_to_docs(request, document_id):
    clients = ClientsReport.objects.get(pk=document_id)
    client_container_text_form = ClientDocFileForm(
        request.POST,
        request.FILES,
        prefix='client_container',
        instance=clients.client_container_doc,
    )
    area_text_form = AreaDocFileForm(
        request.POST,
        request.FILES,
        prefix='area',
        instance=clients.area_doc,
    )
    if client_container_text_form.is_valid():
        client_container_text_form.save()
        if client_container_text_form.has_changed():
            clients.find_n_save_rows()
    if area_text_form.is_valid():
        area_text_form.save()
        if not clients.area_doc:
            clients.area_doc = area_text_form.instance
            clients.save()
        if area_text_form.has_changed():
            clients.add_area_data()
    return HttpResponseRedirect(
        reverse('containers:show_client', args=(document_id,)))




@login_required
def create_client(request):
    if request.method == 'POST':
        client_form = ClientContainer(request.POST, prefix='client_form')
        client_container_file_form = ClientDocFileForm(request.POST, request.FILES,prefix='client_container')
        area_container_file_form = AreaDocFileForm(request.POST, request.FILES,prefix='area_contaienr')
        if client_container_file_form.is_valid():
            client_container_file_form.save()
            client_form.instance.client_container_doc = client_container_file_form.instance
        if area_container_file_form.is_valid():
            print('AREA FORM VALID')
            area_container_file_form.save()
            client_form.instance.area_doc = area_container_file_form.instance
        if client_form.is_valid():
            client_form.save()
            return redirect('containers:clients')
        content = {
            'client_form': client_form,
            'client_container_file_form': client_container_file_form,
            'area_container_file_form': area_container_file_form,
        }
        return render(request, 'containers/clients/create.html', content)
    else:
        client_form = ClientContainer(prefix='client_form')
        client_container_file_form = ClientDocFileForm(prefix='client_container',empty_permitted=True, use_required_attribute=False)
        area_container_file_form = AreaDocFileForm(prefix='area_contaienr', empty_permitted=True, use_required_attribute=False)
        content = {
            'client_form': client_form,
            'client_container_file_form': client_container_file_form,
            'area_container_file_form': area_container_file_form,
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



class WordDocView(ListView):
    model = WordDoc
    context_object_name = 'word_docs'
    template_name = 'containers/word_docs/word_docs.html'


class WordDocCreate(CreateView):
    model = WordDoc
    form_class = WordDocForm
    template_name = 'containers/word_docs/create.html'
    success_url = reverse_lazy('containers:word_docs')


class WordDocUpdate(UpdateView):
    model = WordDoc
    form_class = WordDocForm
    template_name = 'containers/word_docs/create.html'
    success_url = reverse_lazy('containers:word_docs')


def test(request):

    content = {
        'client_container_form': ClientDocFileForm(),
        'area_form': AreaDocFileForm(),
    }
    return render(request, 'containers/test.html', content)


