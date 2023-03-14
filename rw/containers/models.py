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
            # print(reader)
            # print(error)
            pass
    return


class WordDoc(models.Model):
    word_doc_file = models.FileField(upload_to='')
    is_read = models.BooleanField(default=False, editable=False)
    result_text_file = models.FileField(upload_to='', blank=True)
    rows_without_data = models.FileField(blank=True,)

    def save(self, **kwargs):
        if not self.pk:
            super().save()
            self.word_doc_file.name = unidecode(self.word_doc_file.name)
            self.read_word_doc()
        super().save()

    def read_word_doc(self):
        # print('READ', self.word_doc_file.name)
        text = read_doc(self.word_doc_file.path)
        if text:
            self.is_read = True
            self.result_text_file = ContentFile(text, name=self.word_doc_file.name + '_READ.txt')

    def add_rows_without_data(self, text):
        if not self.rows_without_data:
            self.rows_without_data = ContentFile(text, name=self.word_doc_file.name + '__no_data.txt')
        else:
            with open(self.rows_without_data.path, 'w', encoding='utf-8') as file:
                file.write(text)

    def add_result_text(self, text):
        if not self.result_text_file:
            self.result_text_file = ContentFile(text, name='result_text__' + self.word_doc_file.name + '.txt')
        else:
            with open(self.result_text_file.path, 'w', encoding='utf-8') as file:
                file.write(text)

    def add_hand_text(self, text):
        # print('RUN add_hand_text', len(text))
        self.is_read = True
        self.add_result_text(text)
        self.save()

    def get_text(self):
        if self.is_read:
            with open(self.result_text_file.path, encoding='utf-8') as file:
                text = file.read()
            return text
        raise ZeroDivisionError

    def get_no_data_rows(self, unique=True):
        with open(self.rows_without_data.path, encoding='utf-8') as file:
            text =  file.read()
        if unique:
            text = set(text.split('\n'))
            text = '\n'.join(text)
        return text


class ClientDocFile(WordDoc):
    DOC_TYPES = {
        'Книга выгрузки': [93, 109],
        'Книга вывоза': [48, 75]
    }

    class Meta:
        proxy = True

    def get_data(self, doc_type) -> list:
        if not self.is_read:
            return list()
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
        self.add_rows_without_data('\n'.join(rows_without_data))
        self.save()
        return client_container_data


class AreaDocFile(WordDoc):
    class Meta:
        proxy = True

    def get_data(self) -> dict:
        if not self.is_read:
            return dict()
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



    def save(self, **kwargs):
        if not self.pk:
            # print('CLIENT')
            # print(self.client_container_doc)
            super().save()
            self.find_n_save_rows()
            if self.area_doc:
                self.add_area_data()
        else:
            super().save()

    def find_n_save_rows(self):
        if self.client_container_doc:
            client_container_data = self.client_container_doc.get_data(self.client_row_pos)
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

    def update_files_by_hand(self, client_doc_text=None,area_doc_text=None):
        if client_doc_text:
            self.client_container_doc.add_hand_text(client_doc_text)
            self.find_n_save_rows()
        if area_doc_text:
            self.area_doc.add_hand_text(area_doc_text)
            self.add_area_data()

    def add_area_data(self):
        if self.area_doc:
            containers_area = self.area_doc.get_data()
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
    document = models.ForeignKey(ClientDoc, on_delete=models.CASCADE, related_query_name='row', related_name='rows')
    container = models.CharField(max_length=11, )
    client_name = models.CharField(max_length=30)
    date = models.DateField()
    area = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    class Meta:
        ordering = ['client_name', 'date']

    def __str__(self):
        return f'{self.client_name}{self.container}'
