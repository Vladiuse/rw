from django.contrib import admin
from .models import Book


class BookAdmin(admin.ModelAdmin):
    list_display = ['pk', 'type', 'created', 'book_date', 'description']
    list_display_links = ['pk', 'type']


admin.site.register(Book, BookAdmin)
