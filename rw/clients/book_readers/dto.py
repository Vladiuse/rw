from dataclasses import dataclass

@dataclass
class FileContainerExistLines:
    lines_with_container: list
    lines_without_containers: list[str]