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
from .containers.file_mixins import AreaFileMixin, ClientContainerTypeMixin
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Count, Q



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


class ClientDocFile(WordDoc, ClientContainerTypeMixin):
    BOOK_STORE = 'Книга выгрузки'
    BOOK_CALL = 'Книга вывоза'
    DATEFORMAT = '%d.%m.%Y'

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
        result = self.get_data_from_text()
        containers_rows = result['data']
        self.add_rows_without_data('\n'.join(result['rows_without_data']))
        self.save()
        return containers_rows


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
    # clients = models.ManyToManyField('ClientUser', blank=True, related_name='reports', related_query_name='report')

    class Meta:
        ordering = ['-document_date', '-pk']

    def save(self, **kwargs):
        if not self.pk:
            super().save()
            self.find_n_save_rows()
        else:
            super().save()

    def find_n_save_rows(self):
        if self.client_container_doc and self.client_container_doc.can_be_read():
            client_container_data = self.client_container_doc.get_data()
            client_container_to_save = list()
            for item in client_container_data:
                date = datetime.strptime(item['date'],ClientDocFile.DATEFORMAT).date()
                try:
                    area = int(item['area'])
                except ValueError:
                    area = 0
                row = ClientContainerRow(
                    document=self,
                    container=item['container'],
                    client_name=item['client_name'],
                    date=date,
                    nn=item['nn'],
                    weight=item['weight'],
                    send_number=item['send_number'],
                    area=area,
                )
                client_container_to_save.append(row)

            ClientContainerRow.objects.bulk_create(client_container_to_save)

    def client_count(self):
        with connection.cursor() as cursor:
            result_query = self.QUERY % (self.document_date, self.document_date, self.document_date, self.pk)
            cursor.execute(result_query)
            rows = dictfetchall(cursor)
        return rows

    @staticmethod
    def get_admin_reports():
        return ClientsReport.objects.\
            annotate(container_count=Count('row')).order_by('-document_date')

    @staticmethod
    def get_client_reports(client_user):
        return ClientsReport.objects.annotate(container_count=Count(
            'row', Q(row__client_name=client_user.client_filter)
        )).order_by('-document_date')



class ClientContainerRow(models.Model):
    nn = models.CharField(max_length=5)
    send_number = models.CharField(max_length=10)
    weight = models.CharField(max_length=5)
    document = models.ForeignKey(ClientsReport, on_delete=models.CASCADE, related_query_name='row', related_name='rows')
    container = models.CharField(max_length=11, )
    client_name = models.CharField(max_length=30)
    date = models.DateField()
    area = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    class Meta:
        ordering = ['client_name', 'date']


    def save(self, **kwargs):
        self.nn = self.nn.strip()
        self.send_number = self.send_number.strip()
        self.weight = self.weight.strip()
        try:
            self.area = int(self.area)
        except ValueError:
            self.area = None
        super().save()

    def container_number_correct(self):
        container = Container(str(self.container))
        return container.is_container_number_correct()

    def __str__(self):
        return f'{self.client_name}{self.container}'

    def time_delta_past(self):
        return str(timezone.now().date() - self.date + timedelta(days=1)).split(',')[0]


class ClientUser(models.Model):
    #TODO переписать через наследование
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=60, unique=True, verbose_name='Полное имя')
    client_filter = models.CharField(max_length=30, unique=True, verbose_name='Искать по')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.client_name


class FaceProxy(models.Model):
    name = models.CharField(max_length=30)
    attorney = models.CharField(max_length=30)
    client = models.ForeignKey(ClientUser, on_delete=models.SET_NULL,
                               null=True,
                               blank=True,
                               related_name='faces',
                               related_query_name='face',
                               )

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагент'

    def __str__(self):
        return self.name