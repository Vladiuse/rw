from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from .forms import TextBookForm
from .models import Book
from .container_creator import create_containers
from django.views import View
from clients.book_readers.exception import ContainerFileReadError

def index(request):
    return HttpResponse('Clients app')

def book_list(request):
    books = Book.objects.annotate(containers_count=Count('container')).order_by('book_date', '-pk')
    content = {
        'books': books,
    }
    return render(request, 'clients/book_list.html', content)

class LoadBookFileView(View):
    template_name = 'clients/create_book_form.html'

    def get(self, request, *args, **kwargs):
        form = TextBookForm()
        content = {
            'form': form,
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
                book.error_text = error_text
                book.save()
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

def test(request):
    content = {}
    if request.method == 'POST':
        param = request.POST['param']
        if param == 'x':
            messages.success(request,'123')
        content = {
            'param': param,
        }
    return render(request, 'clients/test.html', content)