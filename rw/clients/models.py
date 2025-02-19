from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
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
    error_text = models.TextField(blank=True)


class Container(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='containers', related_query_name='container')
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

    def time_delta_past(self):
        """Время простоя"""
        return str(timezone.now().date() - self.start_date + timedelta(days=1)).split(',')[0]

    def is_past_30(self):
        """Является ли простой больше месяца"""
        diff  = datetime.now().date() - self.start_date
        if diff.days  >= 29:
            return True
        return False