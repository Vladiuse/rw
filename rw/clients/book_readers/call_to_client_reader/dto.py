from dataclasses import dataclass

@dataclass
class ClientRow:
    container_number: str
    start_date: str
    end_date: str
    client_name: str
