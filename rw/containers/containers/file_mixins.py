from .containers_reader import Container
from .errors import AreaFileError


def find(row, positions):
    start, end = positions
    return row[start:end]


class File:

    def __init__(self, text):
        self.text = text
        self.get_rows_without_date = None
        self.result = None

    def get_text(self):
        return self.text

    def get_rows_without_date(self):
        return self.get_rows_without_date

    def get_data_from_text(self):
        text = self.get_text()
        rows_without_data = []
        data = []
        for line in text.split('\n'):
            is_data = self.get_data_from_row(line)
            if is_data:
                data.append(is_data)
            else:
                rows_without_data.append(line)
        result = {
            'rows_without_data': rows_without_data,
            'data': data
        }
        return result


class AreaFileMixin:
    EXAMPLE_ROW = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'

    @staticmethod
    def get_data_from_row(row: str):
        container = Container.find_container_number(row)
        if container:
            row_data = {
                'container': container,
                'area': AreaFileMixin.get_area(row)
            }
            return row_data
        else:
            return None

    @staticmethod
    def get_area(row: str) -> int:
        try:
            area, *other = row.split()
            return int(area)
        except ValueError as error:
            raise AreaFileError('Неудалось найти номер участка', str(error))


class AreaFile(File, AreaFileMixin):
    pass


class ExistBookFileMixin:
    """Книга выгрузки"""

    EXAMPLE_ROW = ' 21164 95236196 31046586     ДОСТЫК (ЭКСП)  MZWU2146680/99 РАДИОДЕТАЛИ           7494        УП ЗЭБТ ГОРИЗОН 05.10.2022 Паламар Е.А. '
    CLIENT_POS = [93, 109]
    NN = [0, 6]
    SEND_NUMBER = [16, 28]

    @staticmethod
    def get_data_from_row(row: str):
        container = Container.find_container_number(row)
        client = ExistBookFileMixin.client(row)
        if container and client:
            row_data = {
                'container': container,
                'client': client,
                'nn': ExistBookFileMixin.nn,
                'send_number': ExistBookFileMixin.send_number,
            }
            return row_data
        else:
            return None

    @staticmethod
    def client(row: str):
        return find(row, ExistBookFileMixin.CLIENT_POS)

    @staticmethod
    def nn(row: str):
        nn = find(row, ExistBookFileMixin.NN)
        return int(nn)

    @staticmethod
    def send_number(row: str):
        send_number = find(row, ExistBookFileMixin.SEND_NUMBER)
        return int(send_number)
