from .containers_reader import Container
from .errors import AreaFileError
import re


def find_date_in_row(row):
    return bool(re.search(r'\d\d\.\d\d.\d{4}', row))


class File:

    def __init__(self, text):
        self.text = text
        self.get_rows_without_date = None
        self.result = None

    def get_text(self):
        return self.text

    def get_rows_without_date(self):
        return self.get_rows_without_date


class ContainerFileMixin:
    ADDITIONAL_DATA = {

    }

    DETECT_VALID_FUNCS = [
        Container.find_container_number,
    ]

    def get_data_from_text(self):
        text = self.get_text()
        rows_without_data = []
        container_area_list = []
        for line in text.split('\n'):
            if self._is_row_valid(line):
                container = Container.find_container_number(line)
                data = self._get_data_from_row(line)
                data['container'] = container
                container_area_list.append(data)
            else:
                rows_without_data.append(line)
        result = {
            'rows_without_data': rows_without_data,
            'data': container_area_list
        }
        return result

    def _is_row_valid(self, row):
        return all([func(row) for func in self.DETECT_VALID_FUNCS])

    def _get_data_from_row(self, row) -> dict:
        data_from_row = dict()
        for key_name, pos in self.ADDITIONAL_DATA.items():
            start, end = pos
            data_from_row.update(
                {key_name: row[start:end].strip()}
            )
        return data_from_row


class AreaFileMixin(ContainerFileMixin):
    EXAMPLE_ROW = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'
    AREA_POS = [0, 2]

    ADDITIONAL_DATA = {
        'area': [0, 2],
    }


class ExistBookFileMixin(ContainerFileMixin):
    """Книга выгрузки"""

    DETECT_VALID_FUNCS = [
        Container.find_container_number,
        find_date_in_row,
    ]

    ADDITIONAL_DATA = {
        'client_name': [93, 109],
        'nn': [0, 6],
        'send_number': [16, 28],
        'date': [109, 119],
        'weight': [77, 85],
        'area': [87, 89],
    }


class CallBookFileMixin(ContainerFileMixin):
    """Книга вывоза"""
    DETECT_VALID_FUNCS = [
        Container.find_container_number,
        find_date_in_row,
    ]
    ADDITIONAL_DATA = {
        'client_name': [48, 75],
        'date': [15, 25],
    }

class ClientContainerTypeMixin(ContainerFileMixin):

    def get_data_from_text(self):
        self.DETECT_VALID_FUNCS = ExistBookFileMixin.DETECT_VALID_FUNCS
        if self.type == 'Книга выгрузки':
            self.ADDITIONAL_DATA = ExistBookFileMixin.ADDITIONAL_DATA
        if self.type == 'Книга вывоза':
            self.ADDITIONAL_DATA = CallBookFileMixin.ADDITIONAL_DATA
        return super().get_data_from_text()
