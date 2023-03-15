import unittest
# from rw.containers.containers.client_counter import *

from datetime import datetime, date, timedelta
from client_counter import ClientReader, ClientContainer, Client
from containers_reader import Container

DATE_FORMAT = '%d.%m.%Y'

today = date.today()
today_str = today.strftime(DATE_FORMAT)
yesterday = today - timedelta(days=1)
yesterday_str = yesterday.strftime(DATE_FORMAT)


class TestClientContainer(unittest.TestCase):

    def setUp(self):
        self.TEXT_3 = """
        ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  6615 98144967 30350661     НАУШКИ КНР ЭКС GESU6166288/99 ИЗДЕЛИЯ ТЕКСТОЛ      25р576  19 171ООО "КОМПАНИЯ К 11.04.2022 Грицкевич М.В.
                             В-СИБ                                                           РОНЕКС"         10:00
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  8346 94868817 0654684      ДРАУГИСТЕ-ПОРТ HDMU2826565/99 ОРГАНИЧЕСКИЕ СО      36216        ЧП ЕВРОРОСТОРГ  10.05.2022 КУЛЬБИЦКАЯ НИНА
                             ЛИТ                                                                             13:00
        контейнера: HDMU2826565/99 HMMU2003689/99
        поп.акты: 1094.
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  8570 94523206 0654210      ДРАУГИСТЕ-ПОРТ TCLU3963131/99 ЖЕЛЕЗА (II) ОКС      20720        СООО "СТАХЕМА-М 14.05.2022 КУЛЬБИЦКАЯ НИНА
                             ЛИТ                                                             "               17:00
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
        """

    def test_find_rows_w_conts(self):
        counter = ClientReader(self.TEXT_3)
        counter.find_client_containers_rows()
        self.assertEqual(len(counter), 3)

    def test_days_past_from_today(self):
        cl_cont = ClientContainer('GESU6166288', yesterday_str, 'SOME')
        self.assertEqual(cl_cont.days_past_from_today, 1)

    # def test_get_days_past_2_digit_date(self):
    #     yesterday = date.today() - timedelta(days=1)
    #     y_str = yesterday.strftime('%d.%m.%y')
    #     row = ClientContainer('GESU6166288', y_str, 'some')
    #     res = row.days_past_from_today
    #     self.assertEqual(res, 1)
    #
    # def test_days_past_from_today_4_digit_date(self):
    #     yesterday = date.today() - timedelta(days=1)
    #     y_str = yesterday.strftime('%d.%m.%Y')
    #     row = ClientContainer('GESU6166288', y_str, 'some')
    #     res = row.days_past_from_today
    #     self.assertEqual(res, 1)

    def test_get_client_name_from_row(self):
        text = '6615 98144967 30350661     НАУШКИ КНР ЭКС GESU6166288/99 ИЗДЕЛИЯ ТЕКСТОЛ      25р576  19 171ООО "КОМПАНИЯ К 11.04.2022 Грицкевич М.В.'
        client = ClientContainer.get_client_name_from_row(text)
        self.assertEqual(client, 'ОО "КОМПАНИЯ К 1')

    def test_find_clients(self):
        reader = ClientReader('')
        reader.client_containers = [
            ClientContainer(Container.A, today_str, Client.CLI_1),
            ClientContainer(Container.A, today_str, Client.CLI_1),
            ClientContainer(Container.A, today_str, Client.CLI_2),
            ClientContainer(Container.A, today_str, Client.CLI_3),
        ]
        reader.find_unique_clients()
        self.assertTrue(len(reader.clients), 3)

    def test_add_client_containers_to_clients(self):
        reader = ClientReader('')
        reader.client_containers = [
            ClientContainer(Container.A, today_str, Client.CLI_1),
            ClientContainer(Container.A, today_str, Client.CLI_1),
            ClientContainer(Container.A, today_str, Client.CLI_2),
            ClientContainer(Container.A, today_str, Client.CLI_2),
            ClientContainer(Container.A, today_str, Client.CLI_3),
            ClientContainer(Container.A, today_str, Client.CLI_3),
        ]
        reader.clients = [
            Client(Client.CLI_1),
            Client(Client.CLI_2),
            Client(Client.CLI_3),
        ]
        reader.add_client_containers_to_clients()
        for client in reader.clients:
            self.assertTrue(len(client), 2)


class TestClient(unittest.TestCase):

    def test_EQ_class(self):
        cli_1 = Client('cli_1')
        cli_2 = Client('cli_1')
        self.assertEqual(cli_1, cli_2)

    def test_not_EQ_class(self):
        cli_1 = Client('cli_1')
        cli_2 = Client('cli_2')
        self.assertNotEqual(cli_1, cli_2)

    def test_EQ_str(self):
        cli_1 = Client('cli_1')
        cli_2 = 'cli_1'
        self.assertEqual(cli_1, cli_2)

    def test_not_EQ_str(self):
        cli_1 = Client('cli_1')
        cli_2 = 'cli_2'
        self.assertNotEqual(cli_1, cli_2)




if __name__ == '__main__':
    unittest.main()
