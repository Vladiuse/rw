from stdnum import iso6346
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from .forms import TextBookForm
from .models import Book, get_col_name_by_book, get_book_stat, get_grouped_by_client_book, get_containers_with_past
from .container_creator import create_containers
from django.views import View
from clients.book_readers.exception import ContainerFileReadError
from .types import BOOK_EXAMPLES


def index(request):
    return HttpResponse('Clients app')

@login_required
def book_list(request):
    books = Book.objects.annotate(containers_count=Count('container')).order_by('-book_date', '-pk')
    content = {
        'books': books,
    }
    return render(request, 'clients/book_list.html', content)

class LoadBookFileView(LoginRequiredMixin, View):
    template_name = 'clients/create_book_form.html'

    def get(self, request, *args, **kwargs):
        form = TextBookForm()
        content = {
            'form': form,
            'book_examples': BOOK_EXAMPLES,
        }
        return render(request, self.template_name, content)

    def post(self, request, *args, **kwargs):
        form = TextBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            try:
                create_containers(book=book)
            except ContainerFileReadError as error:
                error_text = f'Ошибка чтения файла: {error}'
                form.add_error(None, error_text)
                form.data._mutable = True
                form.data['text'] = ''
                book.delete()
                content = {
                    'form': form,
                }
                return render(request, self.template_name, content)
            else:
                containers_count = book.containers.count()
                messages.success(request, f'Книга создана, {containers_count} контейнеров')
                return redirect('clients:book_list')
        else:
            content = {
                'form': form,
            }
            return render(request, self.template_name, content)

@login_required
def book_detail(request, book_id):
    book = Book.objects.get(pk=book_id)
    book_stat = get_book_stat(book=book)
    col_name = get_col_name_by_book(book=book)
    grouped_by_client = get_grouped_by_client_book(book=book)
    containers = get_containers_with_past(book=book)
    containers_no_area = [container for container in containers if container.area is None]
    containers_number_error = [container for container in containers if not iso6346.is_valid(container.number)]
    containers_past_30 = [container for container in containers if container.is_past_30()]
    content = {
        'book': book,
        'book_stat': book_stat,
        'col_name': col_name,
        'grouped_by_client': grouped_by_client,
        'containers': containers,
        'containers_no_area': containers_no_area,
        'containers_number_error': containers_number_error,
        'containers_past_30': containers_past_30,
    }
    return render(request, 'clients/book.html', content)

@login_required
def book_no_containers_data(request, book_id):
    book = Book.objects.get(pk=book_id)
    text = book.no_containers_file.read().decode('utf-8')
    content = {
        'data': text,
    }
    return render(request, 'clients/no_containers_file.html', content)

@login_required
def book_delete(request, book_id):
    book = Book.objects.get(pk=book_id)
    book.delete()
    messages.info(request, 'Книга удалена')
    return redirect('clients:book_list')

def test(request):
    content = {}
    messages.success(request, 'success')
    messages.error(request, 'error')
    messages.warning(request, 'warning')
    messages.info(request, 'info')
    return render(request, 'clients/test.html', content)