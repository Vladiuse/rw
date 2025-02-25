from common.containers.utils import is_line_contain_container
from clients.book_readers.dto import ContainerExistLines

class UploadingBookContainerSeparator:

    def separate(self, lines: list[str]) -> ContainerExistLines:
        lines_with_container = []
        lines_without_containers = []
        book_lines = iter(lines)
        while True:
            try:
                line = next(book_lines)
                if is_line_contain_container(line=line):
                    next_line = next(book_lines)
                    line_with_container = line + '\n' + next_line
                    lines_with_container.append(line_with_container)
                else:
                    lines_without_containers.append(line)
            except StopIteration:
                break
        return ContainerExistLines(
            lines_with_container=lines_with_container,
            lines_without_containers=lines_without_containers,
        )

