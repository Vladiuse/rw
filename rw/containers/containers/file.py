from .containers_reader import Container


class File:

    def __init__(self, text):
        self.text = text
        self.get_rows_without_date = None
        self.result = None


    def get_text(self):
        return self.text

    def get_rows_without_date(self):
        return self.get_rows_without_date






class ClientContainerFileMixin:

    def get_data(self):
        pass



class AreaFileMixin:

    EXAMPLE_ROW = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'


    def get_data_from_text(self):
        text = self.get_text()
        rows_without_data = []
        data = []
        for line in text.split('\n'):
            is_data = AreaFileMixin.get_data_from_row(line)
            if is_data:
                data.append(is_data)
            else:
                rows_without_data.append(line)
        result = {
            'rows_without_data': rows_without_data,
            'data': data
        }
        return result

    @staticmethod
    def get_data_from_row(row:str):
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
    def get_area(row:str) -> int:
        area, *other = row.split()
        return int(area)


class AreaFile(File, AreaFileMixin):
    pass
