from datetime import date, datetime
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from clients.models import (
    Book,
    Container,
    group_containers_by_4_time_periods,
    group_containers_by_day_and_railway,
    group_containers_by_day_night,
)
from clients.types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK


def parse_dt(value: str) -> datetime:
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M")  # noqa: DTZ007
    return timezone.make_aware(dt, timezone.get_current_timezone())


class ContainersCountByDayNightTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(file="123", type=CALL_TO_CLIENTS_BOOK)

    def _create_containers_by_date(self, dates: list[str]) -> None:
        books_to_create = []
        for date_str in dates:
            container = Container(book=self.book, end_date=parse_dt(date_str))
            books_to_create.append(container)
        Container.objects.bulk_create(books_to_create)
        assert Container.objects.count() == len(dates)

    def test_incorrect_book_type(self) -> None:
        book = Mock(spec=Book)
        book.type = UNLOADING_BOOK
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


class RegularAndRailwaysDaysCountTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(file="123", type=CALL_TO_CLIENTS_BOOK)

    def _create_containers_by_date(self, dates: list[str]) -> None:
        books_to_create = []
        for date_str in dates:
            container = Container(book=self.book, end_date=parse_dt(date_str))
            books_to_create.append(container)
        Container.objects.bulk_create(books_to_create)
        assert Container.objects.count() == len(dates)

    def test_(self) -> None:
        dates = (
            "2025-01-01 08:10",  # 2025-01-01
            "2025-01-01 10:10",  # 2025-01-01
            "2025-01-01 20:10",  # 2025-01-02
            "2025-01-02 08:10",  # 2025-01-02
            "2025-01-02 10:10",  # 2025-01-02
            "2025-01-02 20:10",  # 2025-01-03
            "2025-01-03 02:10",  # 2025-01-03
        )
        self._create_containers_by_date(dates=dates)
        result = group_containers_by_day_and_railway(
            book=self.book,
        )
        expected = [
            {"date": date(2025, 1, 1), "total": 3, "railway": 2},
            {"date": date(2025, 1, 2), "total": 3, "railway": 3},
            {"date": date(2025, 1, 3), "total": 1, "railway": 2},
        ]
        assert result == expected, f"actual: {result}"


class FourPeriodForDayTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(file="123", type=CALL_TO_CLIENTS_BOOK)

    def _create_containers_by_date(self, dates: list[str]) -> None:
        books_to_create = []
        for date_str in dates:
            container = Container(book=self.book, end_date=parse_dt(date_str))
            books_to_create.append(container)
        Container.objects.bulk_create(books_to_create)
        assert Container.objects.count() == len(dates)

    def test_(self) -> None:
        dates = (
            "2025-01-01 00:00",
            "2025-01-01 08:00",
            "2025-01-01 08:01",
            "2025-01-01 12:00",
            "2025-01-01 12:01",
            "2025-01-01 12:02",
            "2025-01-01 18:00",
            "2025-01-01 18:01",
            "2025-01-01 18:02",
            "2025-01-01 18:03",
        )
        self._create_containers_by_date(dates=dates)
        result = group_containers_by_4_time_periods(
            book=self.book,
        )
        expected = [
            {"day": date(2025, 1, 1), "c_18_24": 0, "c_0_8": 1, "c_8_12": 2, "c_12_18": 3},
            {"day": date(2025, 1, 2), "c_18_24": 4, "c_0_8": 0, "c_8_12": 0, "c_12_18": 0},
        ]
        assert result == expected, f"actual: {result}"
