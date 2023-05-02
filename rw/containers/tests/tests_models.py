from django.test import TestCase
from containers.models import WordDoc, ClientsReport, ClientContainerRow, ClientDocFile, ClientUser
from django.core.files import File
from django.core.files.base import ContentFile
import shutil
from unittest.mock import MagicMock
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pprint import pprint
from copy import copy
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

TEST_FILES_PATH = '/home/vlad/PycharmProjects/rw/rw/media/test/'


def WRITE_LOG(obj):
    with open('/home/vlad/PycharmProjects/rw/x.txt', 'a') as file:
        if isinstance(obj, (list, set,dict)):
            for i in obj:
                file.write(str(i) + '\n')
            file.write('*'*20 + '\n')
        else:
            file.write(str(obj) + '\n')


class WordDocReadFileTest(TestCase):


    def test_doc_file_redable(self):
        path = '/home/vlad/PycharmProjects/rw/rw/test_files/cli_exist.docx'
        with open(path, 'rb') as fp:
            word_doc = WordDoc()
            word_doc.word_doc_file.save('test/1.docx', File(fp))
            word_doc.save()
        word_doc.check_word_doc()
        self.assertTrue(word_doc.can_be_read())

    def test_doc_file_not_readable(self):
        path = '/home/vlad/PycharmProjects/rw/rw/test_files/1.txt'
        with open(path, 'rb') as fp:
            word_doc = WordDoc()
            word_doc.word_doc_file.save('test/1.txt', File(fp))
            word_doc.save()
        word_doc.check_word_doc()
        self.assertFalse(word_doc.can_be_read())

    def tearDown(self):
        shutil.rmtree(TEST_FILES_PATH)


class GetTextWordDoc(TestCase):

    def setUp(self):
        word_file = ContentFile('Word', name='1.docx')
        txt_file = ContentFile('TXT', name='1.txt')
        self.word_doc = WordDoc.objects.create(word_doc_file='')
        self.word_doc.word_doc_file.save('test/1.docx',word_file)
        self.word_doc.hand_text_file.save('test/1.txt',txt_file)

    def test_return_word_doc_text(self):
        self.word_doc.is_doc_readable = True
        self.word_doc._get_word_doc_text = MagicMock(return_value='123')
        return_text = self.word_doc.get_text()
        self.assertEqual(return_text, '123')

    def test_return_txt_text(self):
        self.word_doc.is_doc_readable = False
        return_text = self.word_doc.get_text()
        self.assertEqual(return_text, 'TXT')

    def test_add_hand_text_data_no_txt_file(self):
        word_file = ContentFile('Word', name='1.docx')
        word_doc = WordDoc.objects.create(word_doc_file='')
        word_doc.word_doc_file.save('test/1.docx',word_file)
        word_doc.add_hand_text('xxx')
        self.assertEqual(word_doc._get_hand_text(), 'xxx')

    def test_add_hand_text_txt_file_exists(self):
        word_file = ContentFile('Word', name='1.docx')
        txt_file = ContentFile('TXT', name='1.txt')
        word_doc = WordDoc.objects.create(word_doc_file='')
        word_doc.word_doc_file.save('test/1.docx',word_file)
        word_doc.hand_text_file.save('test/1.txt',txt_file)
        self.word_doc.is_doc_readable = False
        self.assertEqual(word_doc.get_text(), 'TXT')
        word_doc.add_hand_text('yyy')
        self.assertEqual(word_doc._get_hand_text(), 'yyy')


    def tearDown(self):
        if os.path.exists(TEST_FILES_PATH):
            shutil.rmtree(TEST_FILES_PATH)



class ClientsReportTest(TestCase):

    client_fake_item = {
            'container': 'ABCD1234567',
            'client_name': 'Some name',
            'date': datetime.today().date().strftime(ClientDocFile.DATEFORMAT),
            'nn': 'N/N',
            'weight': '123',
            'send_number': '123',
            'area': '0'
        }



    def setUp(self) -> None:
        word_file = ContentFile('Word', name='1.docx')
        txt_file = ContentFile('TXT', name='1.txt')
        self.word_doc = ClientDocFile.objects.create(word_doc_file='')
        self.word_doc.word_doc_file.save('test/1.docx',word_file)
        self.word_doc.hand_text_file.save('test/1.txt',txt_file)
        self.word_doc.save()
        #
        self.fake_items = [copy(self.client_fake_item) for _ in range(3)]

    def test_find_rows_not_run(self):
        self.word_doc.can_be_read = MagicMock(return_value=False)
        client_report = ClientsReport()
        mock = MagicMock()
        self.word_doc.get_data = mock
        client_report.client_container_doc = self.word_doc
        client_report.save()
        self.assertFalse(mock.called)

    def test_find_words_run(self):
        self.word_doc.can_be_read = MagicMock(return_value=True)
        client_report = ClientsReport()
        mock = MagicMock(return_value=list())
        self.word_doc.get_data = mock
        client_report.client_container_doc = self.word_doc
        client_report.save()
        self.assertEqual(1, mock.call_count)

    def test_create_client_containers_rows(self):
        self.word_doc.can_be_read = MagicMock(return_value=True)
        client_report = ClientsReport()

        fake_data = [self.client_fake_item for _ in range(3)]
        mock = MagicMock(return_value=fake_data)
        self.word_doc.get_data = mock
        # create report
        client_report.client_container_doc = self.word_doc
        client_report.save()

        num_of_rows = ClientContainerRow.objects.count()
        self.assertEqual(num_of_rows,3)

    def test_client_group_count(self):
        NUM = 3
        self.word_doc.can_be_read = MagicMock(return_value=True)
        client_report = ClientsReport()
        fake_data = [self.client_fake_item for _ in range(NUM)]
        mock = MagicMock(return_value=fake_data)
        self.word_doc.get_data = mock
        # create report
        client_report.client_container_doc = self.word_doc
        client_report.save()

        client_group = client_report.client_count()
        self.assertEqual(len(client_group), 1)


    def test_client_group_correct_count(self):
        NUM = 3
        self.word_doc.can_be_read = MagicMock(return_value=True)
        client_report = ClientsReport()
        fake_data = [self.client_fake_item for _ in range(NUM)]
        mock = MagicMock(return_value=fake_data)
        self.word_doc.get_data = mock
        # create report
        client_report.client_container_doc = self.word_doc
        client_report.save()

        client_group = client_report.client_count()
        for row in client_group:
            self.assertEqual(row['count'], NUM)

    def test_time_container_past(self):
        NUM = 3
        self.word_doc.can_be_read = MagicMock(return_value=True)
        client_report = ClientsReport()
        fake_data = copy(self.fake_items)
        #
        for id,item in enumerate(fake_data):
            d = datetime.today().date() - timedelta(days=id +1)
            item['date'] = d.strftime(ClientDocFile.DATEFORMAT)
        #
        mock = MagicMock(return_value=fake_data)
        self.word_doc.get_data = mock
        # create report
        client_report.client_container_doc = self.word_doc
        client_report.save()
        client_group = client_report.client_count()
        row = client_group[0]
        self.assertEqual(row['past'], 2)
        self.assertEqual(row['max'], '3')
        self.assertEqual(row['min'], '1')


    def tearDown(self):
        if os.path.exists(TEST_FILES_PATH):
            shutil.rmtree(TEST_FILES_PATH)


class ClientReportUserAccess(TestCase):

    def setUp(self):
        self.create_users()
        self.create_client_reports()

    def create_users(self):
        self.super_admin = User.objects.create_superuser(username='super', password='0000')
        self.admin = User.objects.create_user(username='admin', password='0000')
        self.cli_user_1 = User.objects.create_user(username='client_1', password='0000')
        self.cli_user_2 = User.objects.create_user(username='client_2', password='0000')
        self.cli_user_3 = User.objects.create_user(username='client_3', password='0000')
        self.client_1 = ClientUser.objects.create(user=self.cli_user_1, client_name='XXX', client_filter='XXX')
        self.client_2 = ClientUser.objects.create(user=self.cli_user_2, client_name='YYY', client_filter='YYY')
        self.client_3 = ClientUser.objects.create(user=self.cli_user_3, client_name='ZZZ', client_filter='ZZZ')
        self.admin_group = Group.objects.create(name='Админы')
        self.admin.groups.add(self.admin_group)

    def create_client_reports(self):
        self.file_1 = ClientDocFile.objects.create(word_doc_file='')
        self.report_1 = ClientsReport.objects.create(client_container_doc=self.file_1)

        self.file_2 = ClientDocFile.objects.create(word_doc_file='')
        self.report_2 = ClientsReport.objects.create(client_container_doc=self.file_2)

        client_rows_reports = []
        for document in self.report_1, self.report_2:
            for client_name in ['XXX', 'XXX', 'YYY']:
                row = ClientContainerRow(
                    document=document,
                    container='ABCD1234567',
                    client_name=client_name,
                    date='2020-10-10',
                    nn='123',
                    weight='123',
                    send_number='123',
                    area='12',
                )
                client_rows_reports.append(row)
        ClientContainerRow.objects.bulk_create(client_rows_reports)

    def test_check(self):
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(ClientDocFile.objects.count(),2)
        self.assertEqual(ClientsReport.objects.count(),2)
        self.assertEqual(ClientContainerRow.objects.count(),6)

    def test_admin_reports(self):
        reports = ClientsReport.get_admin_reports()
        self.assertEqual(len(reports), 2)
        for report in reports:
            self.assertEqual(report.container_count,3)

    def test_client_1_reports(self):
        reports = ClientsReport.get_client_reports(self.client_1)
        self.assertEqual(len(reports), 2)
        for report in reports:
            self.assertEqual(report.container_count,2)

    def test_client_2_reports(self):
        reports = ClientsReport.get_client_reports(self.client_2)
        self.assertEqual(len(reports), 2)
        for report in reports:
            self.assertEqual(report.container_count, 1)



