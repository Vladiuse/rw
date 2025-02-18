import re

CONTAINER_NUMBER_REGEX = '[A-zА-я]{4}\d{7}'


def is_line_contain_container(line: str) -> bool:
    return bool(re.search(CONTAINER_NUMBER_REGEX, line))


def is_container_number_valid(container_number: str) -> bool:
    pass