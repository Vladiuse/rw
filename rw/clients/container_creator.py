from .models import Book, Container
from .types import CALL_TO_CLIENTS_BOOK, UNLOADING_BOOK
from clients.book_readers.call_to_client_reader import ClientCallTextLineConverter
from clients.book_readers.unloading_reader import UnloadingBookTextConverter
from .utils import create_no_containers_file


class CallClientContainerCreator:
    converter = ClientCallTextLineConverter()

    def create(self, book: Book):
        text = book.file.read().decode('utf-8')
        result = self.converter.convert(text=text)
        lines_without_containers_text = '\n'.join(result.lines_without_containers)
        create_no_containers_file(book=book, text=lines_without_containers_text)
        containers_to_create = []
        for container_data in result.lines_with_container:
            container = Container(
                document=book,
                number=container_data.container_number,
                client_name=container_data.client_name,
                start_date=container_data.start_date,
                end_date=container_data.end_date,
            )
            containers_to_create.append(container)
        result = Container.objects.bulk_create(containers_to_create)
        print(result)
        print(type(result))


class UnloadingContainerCreator:
    converter = UnloadingBookTextConverter()

    def create(self, book: Book):
        text = book.file.read().decode('utf-8')
        result = self.converter.convert(text=text)
        lines_without_containers_text = '\n'.join(result.lines_without_containers)
        create_no_containers_file(book=book, text=lines_without_containers_text)
        containers_to_create = []
        for container_data in result.lines_with_container:
            container = Container(
                document=book,
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
        result = Container.objects.bulk_create(containers_to_create)
        print(result)
        print(type(result))



creators = {
    CALL_TO_CLIENTS_BOOK: CallClientContainerCreator(),
    UNLOADING_BOOK: UnloadingContainerCreator(),
}


def create_containers(book: Book):
    creator = creators[book.type]
    creator.create(book=book)
