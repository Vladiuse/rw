from .dto import ClientRow
from clients.book_readers.dto import FileContainerExistLines
from common.containers.utils import is_line_contain_container
from datetime import datetime, date

class ClientCallTextLineConverter:

    def convert(self, text: str) -> FileContainerExistLines:
        lines_with_container = []
        lines_without_containers = []
        lines = text.split('\n')
        for line in lines:
            if is_line_contain_container(line=line):
                item = ClientRow(
                    container_number=self._get_container(line=line),
                    start_date=self._get_start_date(line=line),
                    end_date=self._get_end_date(line=line),
                    client_name=self._get_client_name(line=line)
                )
                lines_with_container.append(item)
            else:
                lines_without_containers.append(line)
        return FileContainerExistLines(
            lines_with_container=lines_with_container,
            lines_without_containers=lines_without_containers,
        )

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

