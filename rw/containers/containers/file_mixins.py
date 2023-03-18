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
        datas = []
        for line in text.split('\n'):
            if self._is_row_valid(line):
                container = Container.find_container_number(line)
                data = self._get_data_from_row(line)
                data['container'] = container
                datas.append(data)
            else:
                rows_without_data.append(line)
        result = {
            'rows_without_data': rows_without_data,
            'data': data
        }
        return result

    def _is_row_valid(self, row):
        return all([func(row) for func in self.DETECT_VALID_FUNCS])

    def _get_data_from_row(self, row) ->dict:
        for key_name, pos in self.ADDITIONAL_DATA.items():
            start, end = pos
            return {
                key_name: row[start:pos].strip()
            }




class AreaFileMixin:
    EXAMPLE_ROW = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'
    AREA_POS = [0,2]

    ADDITIONAL_DATA = {
        'area': [0, 2],
    }




class ExistBookFileMixin:
    """Книга выгрузки"""

    DETECT_VALID_FUNCS = [
        Container.find_container_number,
        find_date_in_row,
    ]

    ADDITIONAL_DATA = {
        'client': [93, 109],
        'nn':  [0, 6],
        'send_number': [16, 28],
        'data':[15,25],
    }

    EXAMPLE_ROW = ' 21164 95236196 31046586     ДОСТЫК (ЭКСП)  MZWU2146680/99 РАДИОДЕТАЛИ           7494        УП ЗЭБТ ГОРИЗОН 05.10.2022 Паламар Е.А. '
    CLIENT_POS = [93, 109]
    NN = [0, 6]
    SEND_NUMBER = [16, 28]
    DATA = [15,25]


