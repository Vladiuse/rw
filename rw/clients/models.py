from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK

class Book(models.Model):
    BOOK_TYPES = (
        (CALL_TO_CLIENTS_BOOK, CALL_TO_CLIENTS_BOOK),
        (UNLOADING_BOOK, UNLOADING_BOOK),
    )
    file = models.FileField(upload_to='books')
    created = models.DateTimeField(auto_now_add=True)
    book_date = models.DateField(default=timezone.now())
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=30, choices=BOOK_TYPES, default=CALL_TO_CLIENTS_BOOK)
    no_containers_file = models.FileField(upload_to='books_no_containers', blank=True)


class Container(models.Model):
    document = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='containers', related_query_name='container')
    number = models.CharField(max_length=11)
    client_name = models.CharField(max_length=30)
    start_date = models.DateField(default=None, null=True)
    end_date = models.DateField(default=None, null=True)
    nn = models.CharField(max_length=5, blank=True)
    send_number = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=5, blank=True)
    area = models.PositiveIntegerField(default=None, null=True, validators=[MaxValueValidator(99)])

    class Meta:
        ordering = ['client_name', 'start_date']