from django.db import models
from django.db.models import F, Count, Min, Max, Avg
from django.db.models.query import QuerySet
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.validators import MaxValueValidator
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK
from django.db import connection
from common.utils import dictfetchall
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK

QUERY = """
SELECT client_name, COUNT(*)as count , 
ROUND(AVG(DATEDIFF('%s', start_date))) as past,
CASE
    WHEN COUNT(*) > 1 THEN MAX( DATEDIFF('%s', start_date))
    ELSE '-'
END as max,
CASE
    WHEN COUNT(*) > 1 THEN MIN( DATEDIFF('%s', start_date))
    ELSE '-'
END as min
FROM clients_container
WHERE book_id = %d
GROUP BY client_name ORDER BY count DESC;
"""



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

    def client_count(self):
        with connection.cursor() as cursor:
            query = QUERY % (self.book_date, self.book_date, self.book_date, self.pk)
            cursor.execute(query)
            rows = dictfetchall(cursor)
        return rows


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
        diff  = datetime.now().date() - self.start_date
        return diff.days >= 29

def get_grouped_by_client_book(book: Book) -> QuerySet[Container]:
    if book.type == CALL_TO_CLIENTS_BOOK:
        end_date = F('end_date')
    elif book.type == UNLOADING_BOOK:
        end_date = timezone.now().date() + timedelta(days=1)
    else:
        raise ValueError('Type for book not found')
    return (
        Container.objects.filter(book=book)
        .annotate(past=end_date - F('start_date'))
        .values('client_name')
        .annotate(count=Count('client_name'))
        .annotate(max=Max('past'))
        .annotate(min=Min('past'))
        .annotate(average_past=Avg('past'))
    )
