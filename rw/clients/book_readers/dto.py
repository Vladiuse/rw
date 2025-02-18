from dataclasses import dataclass
from .call_to_client_reader.dto import CallClientContainer
from .unloading_reader.dto import UploadingContainer

@dataclass
class FileContainerExistLines:
    lines_with_container: list[CallClientContainer | UploadingContainer]
    lines_without_containers: list[str]