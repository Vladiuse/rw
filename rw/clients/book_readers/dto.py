from dataclasses import dataclass

@dataclass
class ContainerExistLines:
    lines_with_container: list[str]
    lines_without_containers: list[str]