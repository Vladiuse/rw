from dataclasses import dataclass
from datetime import date

@dataclass
class UploadingContainer:
    container_number: str
    start_date: date
    client_name: str
    nn: str
    send_number: str
    weight: str
    area: int | None
