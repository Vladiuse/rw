import re
from django.db import models
from django.utils import timezone
from .containers import Container, ClientContainer
from datetime import datetime
from django.db import connection
import os
from unidecode import unidecode

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
        '93:109':'Наличие по получателям',
        '48:75':'Автовывоз',
    }
    CLIENT_POS_IN_ROW = (
        ('93:109', 'Книга выгрузки'),
        ('48:75', 'Книга вывоза'),
    )

    name = models.CharField(max_length=40, verbose_name='Имя документа', default='Без имени', blank=True)
    document = models.TextField(verbose_name='Текст документа',)
    load_date = models.DateField(default=timezone.now, editable=False)
    document_date = models.DateField(default=timezone.now, verbose_name='Дата документа')
    description = models.TextField(blank=True, default='Нет описания', verbose_name='Отписание')
    client_row_pos = models.CharField(max_length=10, choices=CLIENT_POS_IN_ROW, default='93:109',verbose_name='Тип загржаемого файла')
    document_file = models.FileField(upload_to='containers/client_container', blank=True, verbose_name='Исходный документ')

    class Meta:
        ordering = ['-document_date', '-pk']

    def save(self, **kwargs):
        if self.pk:
            super().save()
        else:
            try:
                self.name = self.DOC_NAME[self.client_row_pos]
            except KeyError:
                pass
            self.document_file.name = unidecode(self.document_file.name)
            super().save()
            self.read_doc()

    def docfile_name(self):
        return os.path.basename(str(self.document_file))


    def read_doc(self):
        self.find_n_save_rows()
        self.get_doc_date()

    def find_n_save_rows(self):
        rows = []
        for line in str(self.document).split('\n'):
            cont = Container.find_container_number(line)
            date = re.search(r'\d\d\.\d\d.\d{4}', line)
            pos = str(self.client_row_pos).split(':')
            client_name = ClientContainer.get_client_name_from_row(line, pos)
            if cont and date:
                date = datetime.strptime(date.group(0), '%d.%m.%Y').date()
                row = ClientContainerRow(document=self,container=cont,client_name=client_name,date=date)
                rows.append(row)
        print('END')
        ClientContainerRow.objects.bulk_create(rows)

    def get_doc_date(self):
        pass

    def document_text_rows(self):
        return str(self.document).split('\n')

    def client_count(self):
        with connection.cursor() as cursor:
            result_query = self.QUERY % (self.document_date,self.document_date, self.document_date,self.pk)
            cursor.execute(result_query)
            # rows = cursor.fetchall()
            rows = dictfetchall(cursor)
        return rows



class ClientContainerRow(models.Model):
    document = models.ForeignKey(ClientDoc, on_delete=models.CASCADE, related_query_name='row', related_name='rows')
    container = models.CharField(max_length=11, )
    client_name = models.CharField(max_length=30)
    date = models.DateField()

    class Meta:
        ordering = ['client_name', 'date']

    def __str__(self):
        return f'{self.client_name}{self.container}'

