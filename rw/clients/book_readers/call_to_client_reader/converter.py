from .dto import CallClientContainer
from datetime import datetime, date
from clients.book_readers.exception import FileLineFindDataError

class ClientCallTextLineConverter:

    def convert(self, lines_with_containers: list[str]) -> list[CallClientContainer]:
        call_client_containers = []
        for line in lines_with_containers:
            try:
                item = CallClientContainer(
                    container_number=self._get_container(line=line),
                    start_date=self._get_start_date(line=line),
                    end_date=self._get_end_date(line=line),
                    client_name=self._get_client_name(line=line)
                )
                call_client_containers.append(item)
            except ValueError as error:
                raise FileLineFindDataError(f'Не удалось прочитать строку файла: {error}')
        return call_client_containers

    def _get_container(self, line: str) -> str:
        return line[7:18]

    def _get_start_date(self, line: str) -> date:
        date_string  = line[32:42]
        return datetime.strptime(date_string, '%d.%m.%Y').date()

    def _get_end_date(self, line: str) -> date:
        date_string =  line[49: 59]
        return datetime.strptime(date_string, '%d.%m.%Y').date()

    def _get_client_name(self, line: str) -> str:
        return line[79: 89]

