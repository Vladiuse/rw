from dataclasses import dataclass
from datetime import date

@dataclass
class CallClientContainer:
    container_number: str
    start_date: date
    end_date: date
    client_name: str
