from django.db import models
from django.db.models import F, Count, Min, Max, Avg, ExpressionWrapper
from django.db.models.query import QuerySet
from django.db.models.fields import DurationField, DateField
from django.utils import timezone
from datetime import timedelta, datetime, date
from django.core.validators import MaxValueValidator
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK


class Book(models.Model):
    UNLOADING_BOOK = UNLOADING_BOOK
    CALL_TO_CLIENTS_BOOK = CALL_TO_CLIENTS_BOOK
    BOOK_TYPES = (
        (CALL_TO_CLIENTS_BOOK, CALL_TO_CLIENTS_BOOK),
        (UNLOADING_BOOK, UNLOADING_BOOK),
    )
    file = models.FileField(upload_to='books')
    created = models.DateTimeField(auto_now_add=True)
    book_date = models.DateField(default=timezone.now())
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=30, choices=BOOK_TYPES, default=UNLOADING_BOOK)
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

    def time_delta_past(self):
        """Время простоя"""
        return str(timezone.now().date() - self.start_date + timedelta(days=1)).split(',')[0]

    def is_past_30(self):
        """Является ли простой больше месяца"""
        if self.end_date:
            diff  = self.end_date - self.start_date
        else:
            diff  = datetime.now().date() - self.start_date
        return diff.days >= 29

def get_col_name_by_book(book: Book) -> str:
    if book.type == CALL_TO_CLIENTS_BOOK:
        col_name = 'Вывезено КТК'
    elif book.type == UNLOADING_BOOK:
        col_name = 'Наличие КТК'
    else:
        raise ValueError('Type for book not found')
    return col_name


def get_end_date_by_book_type(book: Book) -> date | F:
    """Получить стартовую дату в зависимости от типа книги"""
    if book.type == CALL_TO_CLIENTS_BOOK:
        end_date = ExpressionWrapper(
            F('end_date') + timedelta(days=1),
            output_field=DateField(),
        )
    elif book.type == UNLOADING_BOOK:
        end_date = timezone.now().date() + timedelta(days=1)
    else:
        raise ValueError('Type for book not found')
    return end_date

def get_grouped_by_client_book(book: Book) -> QuerySet[Container]:
    """Получить данные по контейнерам с групировкой по клиентам"""
    end_date = get_end_date_by_book_type(book=book)
    qs =  (
        Container.objects.filter(book=book)
        .annotate(past=end_date - F('start_date'))
        .values('client_name')
        .annotate(
            count=Count('client_name'),
            max=Max('past'),
            min=Min('past'),
            average_past=Avg('past')
        )
        .order_by('-count', '-average_past')
    )
    return qs

def get_book_stat(book: Book) -> dict:
    """Получить статистику по книге"""
    end_date = get_end_date_by_book_type(book=book)
    return Container.objects.filter(book=book).annotate(past=end_date - F('start_date')).aggregate(
        clients_count=Count('client_name', distinct=True),
        containers_count=Count('number'),
        average_past=Avg('past'),
        max=Max('past'),
        min=Min('past'),
    )

def get_containers_with_past(book: Book) ->  QuerySet[Container]:
    """Получить контейнеры с временем простоя"""
    end_date = get_end_date_by_book_type(book=book)
    return Container.objects.filter(book=book).annotate(past=end_date - F('start_date')).order_by('client_name', '-past')
