import re
from django.db import models
from django.utils import timezone
from .containers import Container, ClientContainer
from datetime import datetime
from django.db import connection
import os
from unidecode import unidecode
from django.core.validators import MaxValueValidator
from django.core.files.base import ContentFile
from .word_doc_reader import read_word_doc


def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


class WordDoc(models.Model):
    word_doc_file = models.FileField(upload_to='', blank=True)
    is_doc_readable = models.BooleanField(default=False, editable=False)
    hand_text_file = models.FileField(upload_to='', blank=True, editable=False)
    rows_without_data = models.FileField(upload_to='', blank=True, editable=False)

    class Meta:
        ordering = ['-pk']

    def delete(self, **kwargs):
        if self.word_doc_file:
            remove_if_exists(self.word_doc_file.path)
        if self.hand_text_file:
            remove_if_exists(self.hand_text_file.path)
        if self.rows_without_data:
            remove_if_exists(self.rows_without_data.path)
        super().delete()

    def can_be_read(self):
        if self.is_doc_readable or self.hand_text_file:
            return True
        return False

    def check_word_doc(self):
        text = read_word_doc(self.word_doc_file.path)
        if text:
            self.is_doc_readable = True
            self.save()

    def add_rows_without_data(self, text):
        if not self.rows_without_data:
            self.rows_without_data = ContentFile(text, name=self.word_doc_file.name + '__no_data.txt')
        else:
            with open(self.rows_without_data.path, 'w', encoding='utf-8') as file:
                file.write(text)

    def add_hand_text(self, text):
        if not self.hand_text_file:
            name = self.word_doc_file.name if self.word_doc_file else ''
            name += '__hand_text.txt'
            self.hand_text_file = ContentFile(text, name=name)
        else:
            with open(self.hand_text_file.path, 'w', encoding='utf-8') as file:
                file.write(text)
        self.save()

    def _get_word_doc_text(self):
        return read_word_doc(self.word_doc_file.path)

    def _get_hand_text(self):
        with open(self.hand_text_file.path, encoding='utf-8') as file:
            return file.read()

    def get_text(self):
        if self.can_be_read():
            if self.is_doc_readable:
                return self._get_word_doc_text()
            else:
                return self._get_hand_text()

    def get_no_data_rows(self, unique=True):
        if self.rows_without_data:
            with open(self.rows_without_data.path, encoding='utf-8') as file:
                text = file.read()
        else:
            text = 'no data'
        if unique:
            text = set(text.split('\n'))
            text = '\n'.join(text)
        return text


class ClientDocFile(WordDoc):
    BOOK_STORE = 'Книга выгрузки'
    BOOK_CALL = 'Книга вывоза'
    DOC_TYPES = (
        (BOOK_STORE, BOOK_STORE),
        (BOOK_CALL, BOOK_CALL),
    )

    CLIENT_NAME_POSITION = {
        BOOK_STORE: [93, 109],
        BOOK_CALL: [48, 75]
    }

    type = models.CharField(
        max_length=30,
        verbose_name='Тип документа',
        choices=DOC_TYPES,
        default=BOOK_STORE,
    )

    def get_data(self) -> list:
        text = self.get_text()
        client_container_data = list()
        rows_without_data = []
        start = ClientDocFile.CLIENT_NAME_POSITION[self.type][0]
        end = ClientDocFile.CLIENT_NAME_POSITION[self.type][1]
        for line in text.split('\n'):
            container = Container.find_container_number(line)
            date = re.search(r'\d\d\.\d\d.\d{4}', line)
            client_name = ClientContainer.get_client_name_from_row(line, (start, end))
            if container and date:
                date = datetime.strptime(date.group(0), '%d.%m.%Y').date()
                dic = {
                    'container': container,
                    'client_name': client_name,
                    'date': date
                }
                client_container_data.append(dic)
            else:
                rows_without_data.append(line)
        self.add_rows_without_data('\n'.join(rows_without_data))
        self.save()
        return client_container_data


class AreaDocFile(WordDoc):
    AREA_TYPE = 'Номера участков'

    type = models.CharField(
        max_length=30,
        verbose_name='Тип документа',
        default=AREA_TYPE,
        editable=False,
    )

    def get_data(self) -> dict:
        text = self.get_text()
        area_data = {}
        rows_without_data = []
        for line in text.split('\n'):
            cont = Container.find_container_number(line)
            if cont:
                area, *other = line.split()
                area_data[cont] = area
            else:
                rows_without_data.append(line)
        self.add_rows_without_data('\n'.join(rows_without_data))
        self.save()
        return area_data


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class ClientsReport(models.Model):
    QUERY = """
    SELECT client_name, COUNT(*)as count , 
    ROUND(AVG(DATEDIFF('%s', date))) as past,
    CASE
        WHEN COUNT(*) > 1 THEN MAX( DATEDIFF('%s', date))
        ELSE '-'
    END as max,
    CASE
        WHEN COUNT(*) > 1 THEN MIN( DATEDIFF('%s', date))
        ELSE '-'
    END as min
    FROM containers_clientcontainerrow
    WHERE document_id = %d
    GROUP BY client_name ORDER BY count DESC;
    """

    DOC_NAME = {
        '93:109': 'Наличие по получателям',
        '48:75': 'Автовывоз',
    }

    CLIENT_POS_IN_ROW = (
        ('Книга выгрузки', 'Книга выгрузки'),
        ('Книга вывоза', 'Книга вывоза'),
    )

    name = models.CharField(
        max_length=40,
        verbose_name='Имя документа',
        default='Без имени',
        blank=True
    )
    document_date = models.DateField(
        default=timezone.now,
        verbose_name='Дата документа'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Отписание'
    )

    client_container_doc = models.OneToOneField(
        ClientDocFile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='client_container_doc',
    )
    area_doc = models.OneToOneField(
        AreaDocFile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Файл с номерами участков',
        related_name='area_doc',
    )

    class Meta:
        ordering = ['-document_date', '-pk']

    def save(self, **kwargs):
        if not self.pk:
            super().save()
            self.find_n_save_rows()
            if self.area_doc:
                self.add_area_data()
        else:
            super().save()

    def find_n_save_rows(self):
        if self.client_container_doc and self.client_container_doc.can_be_read():
            client_container_data = self.client_container_doc.get_data()
            client_container_to_save = list()
            for item in client_container_data:
                row = ClientContainerRow(
                    document=self,
                    container=item['container'],
                    client_name=item['client_name'],
                    date=item['date']
                )
                client_container_to_save.append(row)

            ClientContainerRow.objects.bulk_create(client_container_to_save)
        self.add_area_data()

    def add_area_data(self):
        if self.area_doc and self.area_doc.can_be_read():
            containers_area = self.area_doc.get_data()
            print('AREA len', len(containers_area))
            rows = ClientContainerRow.objects.filter(document=self)
            for row in rows:
                row.area = 0
            ClientContainerRow.objects.bulk_update(rows, ['area'])
            updates_rows = list()
            for client_container_row in rows:
                try:
                    area = containers_area[client_container_row.container]
                    client_container_row.area = area
                    updates_rows.append(client_container_row)
                except KeyError:
                    pass
            ClientContainerRow.objects.bulk_update(updates_rows, ['area'])

    def client_count(self):
        with connection.cursor() as cursor:
            result_query = self.QUERY % (self.document_date, self.document_date, self.document_date, self.pk)
            cursor.execute(result_query)
            # rows = cursor.fetchall()
            rows = dictfetchall(cursor)
        return rows


class ClientContainerRow(models.Model):
    document = models.ForeignKey(ClientsReport, on_delete=models.CASCADE, related_query_name='row', related_name='rows')
    container = models.CharField(max_length=11, )
    client_name = models.CharField(max_length=30)
    date = models.DateField()
    area = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    class Meta:
        ordering = ['client_name', 'date']

    def __str__(self):
        return f'{self.client_name}{self.container}'
