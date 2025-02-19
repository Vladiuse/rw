from datetime import date, datetime
from .dto import UploadingContainer


class UnloadingBookTextConverter:

    def convert(self, lines_with_containers:list[str]) -> list[UploadingContainer]:
        uploading_containers = []
        for line in lines_with_containers:
            item = UploadingContainer(
                container_number=self._get_container(line=line),
                start_date=self._get_start_date(line=line),
                client_name=self._get_client_name(line=line),
                nn=self._get_nn(line=line),
                send_number=self._get_send_number(line=line),
                weight=self._get_weight(line=line),
                area=self._get_area(line=line),
            )
            uploading_containers.append(item)
        return uploading_containers

    def _get_container(self, line: str) -> str:
        return line[44:55]

    def _get_start_date(self, line: str) -> date:
        date_string = line[109:119]
        return datetime.strptime(date_string, '%d.%m.%Y').date()

    def _get_client_name(self, line: str) -> str:
        return line[93: 108]

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
