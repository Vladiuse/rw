from collections import defaultdict
from datetime import date, datetime, timedelta, time

from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Avg, Case, Count, DateField, ExpressionWrapper, F, Max, Min, Q, When
from django.db.models.fields import DateTimeField
from django.db.models.functions import TruncDate
from django.db.models.query import QuerySet
from django.utils import timezone

from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK


class Book(models.Model):
    UNLOADING_BOOK = UNLOADING_BOOK
    CALL_TO_CLIENTS_BOOK = CALL_TO_CLIENTS_BOOK
    BOOK_TYPES = (
        (CALL_TO_CLIENTS_BOOK, CALL_TO_CLIENTS_BOOK),
        (UNLOADING_BOOK, UNLOADING_BOOK),
    )
    file = models.FileField(upload_to="books")
    created = models.DateTimeField(auto_now_add=True)
    book_date = models.DateTimeField(default=timezone.now())
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=30, choices=BOOK_TYPES, default=UNLOADING_BOOK)
    no_containers_file = models.FileField(upload_to="books_no_containers", blank=True)
    error_text = models.TextField(blank=True)


class Container(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="containers", related_query_name="container")
    number = models.CharField(max_length=11)
    client_name = models.CharField(max_length=30)
    start_date = models.DateTimeField(default=None, null=True)
    end_date = models.DateTimeField(default=None, null=True)
    nn = models.CharField(max_length=5, blank=True)
    send_number = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=5, blank=True)
    area = models.PositiveIntegerField(default=None, null=True, validators=[MaxValueValidator(99)])

    def time_delta_past(self) -> str:
        """Время простоя."""
        return str(timezone.now().date() - self.start_date).split(",")[0]

    def is_past_30(self) -> bool:
        """Является ли простой больше месяца."""
        month_day_size = 29
        if hasattr(self, "past"):
            return self.past.days >= month_day_size
        diff = self.end_date - self.start_date if self.end_date else datetime.now().date() - self.start_date
        return diff.days >= month_day_size


def get_col_name_by_book(book: Book) -> str:
    if book.type == CALL_TO_CLIENTS_BOOK:
        col_name = "Вывезено КТК"
    elif book.type == UNLOADING_BOOK:
        col_name = "Наличие КТК"
    else:
        raise ValueError("Type for book not found")
    return col_name


def get_end_date_by_book_type(book: Book) -> date | F:
    """Получить стартовую дату в зависимости от типа книги."""
    if book.type == CALL_TO_CLIENTS_BOOK:
        end_date = ExpressionWrapper(
            F("end_date"),
            output_field=DateTimeField(),
        )
    elif book.type == UNLOADING_BOOK:
        end_date = book.book_date
    else:
        raise ValueError("Type for book not found")
    return end_date


def get_grouped_by_client_book(book: Book) -> QuerySet[Container]:
    """Получить данные по контейнерам с группировкой по клиентам."""
    end_date = get_end_date_by_book_type(book=book)
    return (
        Container.objects.filter(book=book)
        .annotate(past=end_date - F("start_date"))
        .values("client_name")
        .annotate(count=Count("client_name"), max=Max("past"), min=Min("past"), average_past=Avg("past"))
        .order_by("-count", "-average_past")
    )


def get_book_stat(book: Book) -> dict:
    """Получить статистику по книге."""
    end_date = get_end_date_by_book_type(book=book)
    return (
        Container.objects.filter(book=book)
        .annotate(past=end_date - F("start_date"))
        .aggregate(
            clients_count=Count("client_name", distinct=True),
            containers_count=Count("number"),
            average_past=Avg("past"),
            max=Max("past"),
            min=Min("past"),
        )
    )


def get_containers_with_past(book: Book) -> QuerySet[Container]:
    """Получить контейнеры с временем простоя."""
    end_date = get_end_date_by_book_type(book=book)
    return (
        Container.objects.filter(book=book).annotate(past=end_date - F("start_date")).order_by("client_name", "-past")
    )


def group_containers_by_day_night(
    book: Book,
    day_start_at: int,
    night_start_at: int,
) -> list[dict]:
    """Группировка по дням с учетом диапазона день и ночь.

    Пример:
        [
           {'base_day': datetime.date(2025, 1, 1), 'day_count': 3, 'night_count': 3},
           {'base_day': datetime.date(2025, 1, 2), 'day_count': 3, 'night_count': 2}
        ]
    """
    if book.type != CALL_TO_CLIENTS_BOOK:
        msg = f"Incorrect book type. must be {CALL_TO_CLIENTS_BOOK}"
        raise TypeError(msg)
    if day_start_at >= night_start_at:
        raise ValueError('"day_start_at" must be less that "night_start_at"')
    shifted_dt = ExpressionWrapper(
        F("end_date") - timedelta(days=1),
        output_field=DateTimeField(),
    )

    return list(
        Container.objects.filter(book=book)
        .annotate(
            base_day=Case(
                When(end_date__hour__lt=day_start_at, then=TruncDate(shifted_dt)),
                default=TruncDate("end_date"),
                output_field=DateField(),
            ),
        )
        .values("base_day")
        .annotate(
            day_count=Count(
                "id",
                filter=Q(end_date__hour__gte=day_start_at, end_date__hour__lt=night_start_at),
            ),
            night_count=Count(
                "id",
                filter=Q(end_date__hour__gte=night_start_at) | Q(end_date__hour__lt=day_start_at),
            ),
        )
        .order_by("base_day"),
    )


def group_containers_by_day_and_railway(book: Book) -> list[dict]:
    """Группировка по обычному дню и железнодорожному дню (18:00–18:00).

    Возвращает таблицу с колонками:
        - date: календарная дата
        - total: количество контейнеров за этот день
        - railway: количество контейнеров за железнодорожный день (18:00 предыдущего дня - 18:00 текущего)
    """
    if book.type != CALL_TO_CLIENTS_BOOK:
        msg = f"Incorrect book type. must be {CALL_TO_CLIENTS_BOOK}"
        raise TypeError(msg)
    calendar_count = defaultdict(int)
    railway_count = defaultdict(int)
    containers = Container.objects.filter(book=book)
    for container in containers:
        # календарный день
        calendar_date = container.end_date.date()
        calendar_count[calendar_date] += 1

        # железнодорожный день
        # если время > 18:00, относим к предыдущему дню
        rail_date = (
            (container.end_date + timedelta(days=1)).date()
            if container.end_date.time() > time(18, 0)
            else container.end_date.date()
        )
        railway_count[rail_date] += 1

    # объединяем все даты
    all_dates = sorted(set(calendar_count.keys()) | set(railway_count.keys()))

    return [
        {
            "date": d,
            "total": calendar_count.get(d, 0),
            "railway": railway_count.get(d, 0),
        }
        for d in all_dates
    ]
