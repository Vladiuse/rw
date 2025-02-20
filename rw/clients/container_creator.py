from .models import Book, Container
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK
from clients.book_readers.call_to_client_reader import ClientCallTextLineConverter
from clients.book_readers.unloading_reader import UnloadingBookTextConverter
from .utils import create_no_containers_file
from clients.book_readers.container_separator import ContainerSeparator
from clients.book_readers.exception import ContainerNotFound

class ContainerCreatorFromBook:
    """Класс для создания контейнеров по данным из книги"""
    separator = ContainerSeparator()

    def create_containers_items(self, book: Book, lines_with_container: list[str]) -> list[Container]:
        raise NotImplementedError

    def create(self, book: Book):
        text = book.file.read().decode('utf-8')
        separated_lines = self.separator.separate(lines=text.split('\n'))
        if len(separated_lines.lines_with_container) == 0:
            raise ContainerNotFound('В файле не найдены строки с контейнерами')
        containers_to_create = self.create_containers_items(book=book, lines_with_container=separated_lines.lines_with_container)
        res = Container.objects.bulk_create(containers_to_create)
        print(res)
        print(type(res))
        no_container_text = '\n'.join(separated_lines.lines_without_containers)
        create_no_containers_file(book=book, text=no_container_text)



class CallClientContainerCreator(ContainerCreatorFromBook):
    converter = ClientCallTextLineConverter()

    def create_containers_items(self, book: Book,lines_with_container: list[str]):
        containers_data = self.converter.convert(lines_with_containers=lines_with_container)
        containers_to_create = []
        for container_data in containers_data:
            container = Container(
                book=book,
                number=container_data.container_number,
                client_name=container_data.client_name,
                start_date=container_data.start_date,
                end_date=container_data.end_date,
            )
            containers_to_create.append(container)
        return containers_to_create


class UnloadingContainerCreator(ContainerCreatorFromBook):
    converter = UnloadingBookTextConverter()

    def create_containers_items(self, book: Book,lines_with_container: list[str]):
        containers_data = self.converter.convert(lines_with_containers=lines_with_container)
        containers_to_create = []
        for container_data in containers_data:
            container = Container(
                book=book,
                number=container_data.container_number,
                client_name=container_data.client_name,
                start_date=container_data.start_date,
                end_date=None,
                nn=container_data.nn,
                send_number=container_data.send_number,
                weight=container_data.weight,
                area=container_data.area,
            )
            containers_to_create.append(container)
        return containers_to_create


creators = {
    CALL_TO_CLIENTS_BOOK: CallClientContainerCreator(),
    UNLOADING_BOOK: UnloadingContainerCreator(),
}

def create_containers(book: Book):
    """Создать контейнеры для книги"""
    creator = creators[book.type]
    creator.create(book=book)
