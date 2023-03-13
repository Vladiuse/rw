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
import docx2txt
import textract


def read_one(path):
    text = docx2txt.process(path)
    return text


def read_two(path):
    text = textract.process(path)
    text = text.decode('utf-8')
    return text


def read_doc(path):
    for reader in read_one, read_two:
        try:
            text = reader(path)
            return text
        except BaseException as error:
            print(reader)
            print(error)
    return


class WordDoc(models.Model):
    doc_file = models.FileField(upload_to='')
    is_read = models.BooleanField(default=False, editable=False)
    text_file = models.FileField(upload_to='', blank=True)
    rows_without_data = models.TextField(blank=True,)

    def save(self, **kwargs):
        if not self.pk:
            super().save()
            self.doc_file.name = unidecode(self.doc_file.name)
            self.read()
        super().save()

    def read(self):
        text = read_doc(self.doc_file.path)
        if text:
            self.is_read = True
            self.text_file = ContentFile(text, name=self.doc_file.name + '.txt')

    def add_hand_text(self, text):
        self.is_read = True
        self.text_file = ContentFile(text, name=self.doc_file.name + '.txt')
        self.save()

    def get_text(self):
        if self.is_read:
            with open(self.text_file.path) as file:
                text = file.read()
            return text
        raise ZeroDivisionError


class ClientDocFile(WordDoc):
    DOC_TYPES = {
        'Книга выгрузки': [93, 109],
        'Книга вывоза': [48, 75]
    }

    class Meta:
        proxy = True

    def get_data(self, doc_type) -> list:
        text = self.get_text()
        client_container_data = list()
        rows_without_data = []
        start = ClientDocFile.DOC_TYPES[doc_type][0]
        end = ClientDocFile.DOC_TYPES[doc_type][1]
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
        self.rows_without_data = '\n'.join(rows_without_data)
        self.save()
        return client_container_data


class AreaDocFile(WordDoc):
    class Meta:
        proxy = True

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
        self.rows_without_data = '\n'.join(rows_without_data)
        self.save()
        return area_data

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class ClientDoc(models.Model):
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
    #     ('93:109', 'Книга выгрузки'),
    #     ('48:75', 'Книга вывоза'),

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
    client_row_pos = models.CharField(
        max_length=20,
        choices=CLIENT_POS_IN_ROW,
        default='93:109',
        verbose_name='Тип загржаемого файла'
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

    # def save(self, **kwargs):
    #     if self.pk:
    #         super().save()
    #     else:
    #         try:
    #             self.name = self.DOC_NAME[self.client_row_pos]
    #         except KeyError:
    #             pass
    #         self.document_file.name = unidecode(self.document_file.name)
    #         super().save()
    #         # self.read_doc()
    #
    # def docfile_name(self):
    #     return os.path.basename(str(self.document_file))

    # def read_doc(self):
    #     self.find_n_save_rows()
    #     self.add_area_data()

    # def find_n_save_rows(self):
    #     rows = []
    #     text = read_doc(self.document_file.path)
    #     if text:
    #         for line in text.split('\n'):
    #             cont = Container.find_container_number(line)
    #             date = re.search(r'\d\d\.\d\d.\d{4}', line)
    #             pos = str(self.client_row_pos).split(':')
    #             client_name = ClientContainer.get_client_name_from_row(line, pos)
    #             if cont and date:
    #                 date = datetime.strptime(date.group(0), '%d.%m.%Y').date()
    #                 row = ClientContainerRow(document=self,container=cont,client_name=client_name,date=date)
    #                 rows.append(row)
    #         print('END')
    #         ClientContainerRow.objects.bulk_create(rows)

    def get_doc_date(self):
        pass

    # def add_area_data(self):
    #     if self.area_document:
    #         text = read_doc(self.area_document.path)
    #         if text:
    #             rows = ClientContainerRow.objects.filter(document=self)
    #             for row in rows:
    #                 row.area = 0
    #             ClientContainerRow.objects.bulk_update(rows, ['area'])
    #             area_data = {}
    #             for line in text.split('\n'):
    #                 cont = Container.find_container_number(line)
    #                 if cont:
    #                     area, *other = line.split()
    #                     area_data[cont] = area
    #             updates_rows = []
    #             for client_container_row in rows:
    #                 try:
    #                     area = area_data[client_container_row.container]
    #                     client_container_row.area = area
    #                     updates_rows.append(client_container_row)
    #                 except KeyError:
    #                     pass
    #             ClientContainerRow.objects.bulk_update(updates_rows, ['area'])

    def client_count(self):
        with connection.cursor() as cursor:
            result_query = self.QUERY % (self.document_date, self.document_date, self.document_date, self.pk)
            cursor.execute(result_query)
            # rows = cursor.fetchall()
            rows = dictfetchall(cursor)
        return rows


class ClientContainerRow(models.Model):
    document = models.ForeignKey(ClientDoc, on_delete=models.CASCADE, related_query_name='row', related_name='rows')
    container = models.CharField(max_length=11, )
    client_name = models.CharField(max_length=30)
    date = models.DateField()
    area = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    class Meta:
        ordering = ['client_name', 'date']

    def __str__(self):
        return f'{self.client_name}{self.container}'
