from clients.models import Book, Container
from clients.container_creator import create_containers


Container.objects.all().delete()
books = Book.objects.all()
for book in books:
    create_containers(book=book)