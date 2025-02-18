from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from .forms import TextBookForm
from .models import Book
from .container_creator import create_containers

def index(request):
    return HttpResponse('Clients app')

def book_list(request):
    books = Book.objects.annotate(containers_count=Count('container')).order_by('book_date', '-pk')
    content = {
        'books': books,
    }
    return render(request, 'clients/book_list.html', content)

def load_book_file(request):
    if request.method == 'POST':
        form = TextBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            try:
                create_containers(book=book)
            except Exception as error:
                error_text = f'Ошибка чтения файла: {type(error)}:{error}'
                form.add_error(None, error_text)
                form.data._mutable = True
                form.data['text'] = ''
                book.error_text = error_text
                book.save()
            else:
                containers_count = book.containers.count()
                messages.success(request, f'Книга создана, {containers_count} контейнеров')
                return redirect('clients:book_list')
        content = {
            'form': form,
        }
        return render(request, 'clients/create_book_form.html', content)
    form = TextBookForm()
    content = {
        'form': form,
    }
    return render(request, 'clients/create_book_form.html', content)


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