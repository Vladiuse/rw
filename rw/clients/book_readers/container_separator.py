from common.containers.utils import is_line_contain_container
from .dto import ContainerExistLines


class ContainerSeparator:
    """Separate text lines by container exists"""

    def separate(self, lines: list[str]) -> ContainerExistLines:
        lines_with_container = []
        lines_without_containers = []
        for line in lines:
            if is_line_contain_container(line=line):
                lines_with_container.append(line)
            else:
                lines_without_containers.append(line)
        return ContainerExistLines(
            lines_with_container=lines_with_container,
            lines_without_containers=lines_without_containers,
        )
