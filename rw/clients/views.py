from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from .forms import TextBookForm
from .models import Book

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
            form.save()
            return HttpResponse('SUCCESS')
        content = {
            'form': form,
        }
        return render(request, 'clients/create_book_form.html', content)
    form = TextBookForm()
    content = {
        'form': form,
    }
    return render(request, 'clients/create_book_form.html', content)