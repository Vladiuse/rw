from datetime import date, datetime
from unittest.mock import Mock

from clients.models import Book, Container, group_containers_by_day_night
from clients.types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK
from django.test import TestCase
from django.utils import timezone


def parse_dt(value: str) -> datetime:
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M")  # noqa: DTZ007
    return timezone.make_aware(dt, timezone.get_current_timezone())


class ContainersCountByDayNightTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(file="123", type=UNLOADING_BOOK)

    def _create_containers_by_date(self, dates: list[str]) -> None:
        books_to_create = []
        for date_str in dates:
            container = Container(book=self.book, end_date=parse_dt(date_str))
            books_to_create.append(container)
        Container.objects.bulk_create(books_to_create)
        assert Container.objects.count() == len(dates)

    def test_incorrect_book_type(self) -> None:
        book = Mock(spec=Book)
        book.type = CALL_TO_CLIENTS_BOOK
        with self.assertRaises(TypeError):
            group_containers_by_day_night(book=book, day_start_at=8, night_start_at=20)

    def test_one_day(self) -> None:
        dates = (
            "2025-01-01 08:00",
            "2025-01-01 10:00",
            "2025-01-01 20:00",
            "2025-01-02 00:00",
            "2025-01-02 04:00",
        )
        self._create_containers_by_date(dates=dates)
        result = group_containers_by_day_night(book=self.book, day_start_at=8, night_start_at=20)
        expected = [
            {"base_day": date(2025, 1, 1), "day_count": 2, "night_count": 3},
        ]
        assert result == expected, f"actual: {result}"

    def test_few_days(self) -> None:
        dates = (
            "2025-01-01 08:10",
            "2025-01-01 10:10",
            "2025-01-01 20:10",
            "2025-01-02 00:10",
            "2025-01-02 04:10",
            "2025-01-02 07:59",
            "2025-01-02 08:00",
            "2025-01-02 16:00",
            "2025-01-02 20:00",
            "2025-01-03 00:00",
            "2025-01-03 04:00",
        )
        self._create_containers_by_date(dates=dates)
        result = group_containers_by_day_night(book=self.book, day_start_at=8, night_start_at=20)
        expected = [
            {"base_day": date(2025, 1, 1), "day_count": 2, "night_count": 4},
            {"base_day": date(2025, 1, 2), "day_count": 2, "night_count": 3},
        ]
        assert result == expected, f"actual: {result}"
