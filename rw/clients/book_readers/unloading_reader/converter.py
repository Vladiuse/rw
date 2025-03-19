from datetime import date, datetime
from .dto import UploadingContainer
from clients.book_readers.exception import FileLineFindDataError

class UnloadingBookTextConverter:
    CLIENT_TEXT_POSITION = (93, 108)

    def convert(self, lines_with_containers:list[str]) -> list[UploadingContainer]:
        uploading_containers = []
        for line_num, paired_line in enumerate(lines_with_containers):
            header_line, footer_line = paired_line.split('\n')
            try:
                item = UploadingContainer(
                    container_number=self._get_container(line=header_line),
                    start_date=self._get_start_date(line=header_line),
                    client_name=self._get_client_name(header_line=header_line, footer_line=footer_line),
                    nn=self._get_nn(line=header_line),
                    send_number=self._get_send_number(line=header_line),
                    weight=self._get_weight(line=header_line),
                    area=self._get_area(line=header_line),
                )
                uploading_containers.append(item)
            except ValueError as error:
                error_message = f'Не удалось прочитать строку файла #{line_num + 1}: {error} \n{header_line}'
                raise FileLineFindDataError(error_message)
        return uploading_containers

    def _get_container(self, line: str) -> str:
        return line[44:55]

    def _get_start_date(self, line: str) -> date:
        date_string = line[109:119]
        return datetime.strptime(date_string, '%d.%m.%Y').date()

    def _get_client_name(self, header_line: str, footer_line: str) -> str:
        start, end = UnloadingBookTextConverter.CLIENT_TEXT_POSITION
        client_name = header_line[start: end] + footer_line[start: end]
        return client_name.strip()

    def _get_nn(self, line: str) -> str:
        return line[0: 6].strip()

    def _get_send_number(self, line: str) -> str:
        return line[16: 28].strip()

    def _get_weight(self, line: str) -> str:
        return line[77: 85].strip()

    def _get_area(self, line: str) -> int | None:
        area = line[87: 89].strip()
        if area == '':
            return None
        return int(area)
