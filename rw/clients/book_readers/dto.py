from dataclasses import dataclass
from .call_to_client_reader.dto import ClientRow

@dataclass
class FileContainerExistLines:
    lines_with_container: list[ClientRow]
    lines_without_containers: list[str]