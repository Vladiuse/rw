from datetime import datetime
from common.utils import get_random_file_name

def get_name_for_book_file(date: datetime = None, book_type: str = None) -> str:
    if all((date, book_type)):
        return f'{date}_{book_type}_{get_random_file_name()}.txt'
    return get_random_file_name() + '.txt'
