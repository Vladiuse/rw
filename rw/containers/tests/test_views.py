from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from containers.models import WordDoc, ClientsReport, ClientContainerRow, ClientDocFile, ClientUser,FaceProxy
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from unittest.mock import MagicMock, patch
from django.core.exceptions import ObjectDoesNotExist


class TestViews(TestCase):

    def setUp(self):
        self.create_users()
        self.create_client_reports()
        self.test_create_face_proxy()

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

    def test_create_face_proxy(self):
        self.face_1 = FaceProxy.objects.create(name='1',attorney='1', client=self.client_1)
        self.face_2 = FaceProxy.objects.create(name='2',attorney='2', client=self.client_1)
        self.face_3 = FaceProxy.objects.create(name='3',attorney='3', client=self.client_2)

    def test_check(self):
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(ClientDocFile.objects.count(),2)
        self.assertEqual(ClientsReport.objects.count(),2)
        self.assertEqual(ClientContainerRow.objects.count(),6)
        self.assertEqual(FaceProxy.objects.count(),3)

        self.admin.groups.filter(name='Админы').exists()


    def test_client_docs_list_not_login(self):
        res = self.client.get(reverse('containers:clients'))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, settings.LOGIN_URL + '?next=' +reverse('containers:clients'))
        self.assertTemplateNotUsed(res, 'containers/clients/clients.html')

    def test_client_doc_list_log_in(self):
        for user in self.admin, self.cli_user_1:
            self.client.login(
                username=user.username,password='0000'
            )
            res = self.client.get(reverse('containers:clients'))
            self.assertEqual(res.status_code, 200)
            self.assertTemplateUsed(res, 'containers/clients/clients.html')

            self.client.logout()

    def test_client_doc_list_admin_func_call(self):
        self.client.login(
            username=self.admin.username, password='0000'
        )
        with patch('containers.models.ClientsReport.get_admin_reports') as admin_mock:
            with patch('containers.models.ClientsReport.get_client_reports') as client_mock:
                res = self.client.get(reverse('containers:clients'))
                self.assertEqual(res.status_code, 200)
                self.assertTemplateUsed(res, 'containers/clients/clients.html')
                self.assertTrue(admin_mock.called)
                self.assertFalse(client_mock.called)

    def test_client_doc_list_client_user_func_call(self):
        self.client.login(
            username=self.cli_user_1.username, password='0000'
        )
        with patch('containers.models.ClientsReport.get_admin_reports') as admin_mock:
            with patch('containers.models.ClientsReport.get_client_reports') as client_mock:
                res = self.client.get(reverse('containers:clients'))
                self.assertEqual(res.status_code, 200)
                self.assertTemplateUsed(res, 'containers/clients/clients.html')
                self.assertFalse(admin_mock.called)
                self.assertTrue(client_mock.called)

    def test_report_superadmin_request(self):
        self.client.login(
            username=self.super_admin.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]))
        self.assertTemplateUsed(res, 'containers/clients/client.html')

    def test_report_admin_request(self):
        self.client.login(
            username=self.admin.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]))
        self.assertTemplateUsed(res, 'containers/clients/client.html')

    def test_report_client_request(self):
        self.client.login(
            username=self.cli_user_1.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]))
        self.assertRedirects(res, reverse('containers:client_document', args=[self.report_1.pk]))


    def test_report_superadmin_rows(self):
        self.client.login(
            username=self.super_admin.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]))
        self.assertEqual(len(res.context['rows']), 3)


    def test_report_admin_rows(self):
        self.client.login(
            username=self.admin.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]))
        self.assertEqual(len(res.context['rows']), 3)

    def test_report_client_1_rows(self):
        self.client.login(
            username=self.cli_user_1.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]), follow=True)
        self.assertEqual(len(res.context['rows']), 2)

    def test_report_client_2_rows(self):
        self.client.login(
            username=self.cli_user_2.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]), follow=True)
        self.assertEqual(len(res.context['rows']), 1)

    def test_report_client_3_rows(self):
        self.client.login(
            username=self.cli_user_3.username, password='0000'
        )
        res = self.client.get(reverse('containers:show_client', args=[self.report_1.pk]), follow=True)
        self.assertEqual(len(res.context['rows']), 0)

    def test_print_document(self):
        self.client.login(
            username=self.cli_user_1.username, password='0000'
        )
        client_row_data = {
            'container' : 'ABCD1234567',
            'nn' : 'NN',
            'weight' : '999',
            'area' : '13',
        }
        row = ClientContainerRow.objects.create(
                    document=self.report_1,
                    client_name='client_name',
                    date= '2020-10-10',
                    send_number= '666',
                    **client_row_data
                )
        res = self.client.get(reverse('containers:print_document', args=[row.pk]))
        for val in client_row_data.values():
            self.assertContains(res, val)

    def test_document_print_face_proxy(self):
        for user in [self.cli_user_1, self.cli_user_2, self.cli_user_3]:
            self.client.login(
                username=user.username, password='0000'
            )
            row = ClientContainerRow.objects.last()
            res = self.client.get(reverse('containers:print_document', args=[row.pk]))
            faces = res.context['faces']
            client = ClientUser.objects.get(user=user)
            self.assertQuerysetEqual(faces, client.faces.all())


    def test_admin_view_doc(self):
        self.client.login(
            username=self.admin.username, password='0000'
        )
        res = self.client.get(reverse('containers:client_document', args=[self.report_1.pk]))
        self.assertEqual(res.status_code, 404)

