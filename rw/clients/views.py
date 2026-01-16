from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from stdnum import iso6346

from clients.book_readers.exception import ContainerFileReadError

from .container_creator import create_containers
from .forms import TextBookForm
from .models import (
    Book,
    get_book_stat,
    get_col_name_by_book,
    get_containers_with_past,
    get_grouped_by_client_book,
    group_containers_by_day_and_railway,
    group_containers_by_day_night,
)
from .types import BOOK_EXAMPLES, CALL_TO_CLIENTS_BOOK


def index(request: HttpRequest) -> HttpResponse:
    _ = request
    return HttpResponse("Clients app")


@login_required
def book_list(request: HttpRequest) -> HttpResponse:
    books = Book.objects.annotate(containers_count=Count("container")).order_by("-book_date", "-pk")
    content = {
        "books": books,
    }
    return render(request, "clients/book/book_list.html", content)


class LoadBookFileView(LoginRequiredMixin, View):
    template_name = "clients/book/create_book.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003
        (
            _,
            _,
        ) = args, kwargs
        form = TextBookForm()
        content = {
            "form": form,
            "book_examples": BOOK_EXAMPLES,
        }
        return render(request, self.template_name, content)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003
        (
            _,
            _,
        ) = args, kwargs
        form = TextBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            try:
                create_containers(book=book)
            except ContainerFileReadError as error:
                error_text = f"Ошибка чтения файла: {error}"
                form.add_error(None, error_text)
                form.data._mutable = True
                form.data["text"] = ""
                book.delete()
                content = {
                    "form": form,
                }
                return render(request, self.template_name, content)
            else:
                containers_count = book.containers.count()
                messages.success(request, f"Книга создана, {containers_count} контейнеров")
                return redirect("clients:book_list")
        else:
            content = {
                "form": form,
            }
            return render(request, self.template_name, content)


@login_required
def book_detail(request: HttpRequest, book_id: int) -> HttpResponse:
    book = Book.objects.get(pk=book_id)
    book_stat = get_book_stat(book=book)
    col_name = get_col_name_by_book(book=book)
    grouped_by_client = get_grouped_by_client_book(book=book)
    containers = get_containers_with_past(book=book)
    containers_no_area = [container for container in containers if container.area is None]
    containers_number_error = [container for container in containers if not iso6346.is_valid(container.number)]
    containers_past_30 = [container for container in containers if container.is_past_30()]
    day_night_8 = (
        group_containers_by_day_night(book=book, day_start_at=8, night_start_at=20)
        if book.type == CALL_TO_CLIENTS_BOOK
        else []
    )
    day_night_6 = (
        group_containers_by_day_night(book=book, day_start_at=6, night_start_at=18)
        if book.type == CALL_TO_CLIENTS_BOOK
        else []
    )
    day_and_railway_day_count = (
        group_containers_by_day_and_railway(book=book)
        if book.type == CALL_TO_CLIENTS_BOOK
        else []
    )
    content = {
        "book": book,
        "book_stat": book_stat,
        "col_name": col_name,
        "grouped_by_client": grouped_by_client,
        "containers": containers,
        "containers_no_area": containers_no_area,
        "containers_number_error": containers_number_error,
        "containers_past_30": containers_past_30,
        "day_night_8": day_night_8,
        "day_night_6": day_night_6,
        "day_and_railway_day_count": day_and_railway_day_count,
    }
    return render(request, "clients/book/book_detail.html", content)


@login_required
def book_no_containers_data(request: HttpRequest, book_id: int) -> HttpResponse:
    _ = request
    book = Book.objects.get(pk=book_id)
    text = book.no_containers_file.read().decode("utf-8")
    return HttpResponse(f"<pre>{text}</pre>")


@login_required
def book_file_original_text(request: HttpRequest, book_id: int) -> HttpResponse:
    _ = request
    book = Book.objects.get(pk=book_id)
    text = book.file.read().decode("utf-8")
    return HttpResponse(f"<pre>{text}</pre>")


@login_required
def book_delete(request: HttpRequest, book_id: int) -> HttpResponse:
    book = Book.objects.get(pk=book_id)
    book.delete()
    messages.info(request, "Книга удалена")
    return redirect("clients:book_list")


def test(request: HttpRequest) -> HttpResponse:
    content = {}
    messages.success(request, "success")
    messages.error(request, "error")
    messages.warning(request, "warning")
    messages.info(request, "info")
    return render(request, "clients/test.html", content)
