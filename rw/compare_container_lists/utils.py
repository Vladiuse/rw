from .types import reader_types


def get_reader_by_type(type: str):
    return reader_types[type]