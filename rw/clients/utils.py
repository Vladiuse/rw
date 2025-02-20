from django.core.files.base import ContentFile
from .models import Book
from datetime import datetime
from common.utils import get_random_file_name

def get_name_for_book_file(date: datetime = None, book_type: str = None) -> str:
    """Получить рандомное имя для файла книги"""
    if all((date, book_type)):
        return f'{date}_{book_type}_{get_random_file_name()}.txt'
    return get_random_file_name() + '.txt'


def create_no_containers_file(book: Book, text: str) -> None:
    """Создать файл со строками без контейнеров для книги"""
    no_containers_file = ContentFile(text)
    book.no_containers_file.save('no_conts.txt', no_containers_file, save=True)
