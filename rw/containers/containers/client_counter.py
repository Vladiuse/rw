from .containers_reader import Container
import re
from datetime import datetime, date
import json

class ClientContainer:

    def __init__(self, container_id, date, client_name, ):
        self.id = container_id
        self.date = datetime.strptime(date, '%d.%m.%Y').date()
        self.client_name = client_name
        self.past = self.days_past_from_today

    @property
    def days_past_from_today(self):
        return (date.today() - self.date).days

    @staticmethod
    def get_client_name_from_row(text_row, pos):
        start, end = pos
        start, end = int(start), int(end)
        return text_row[start:end]
        # return text_row[93:109]


class Client:
    CLI_1 = 'cli_1'
    CLI_2 = 'cli_2'
    CLI_3 = 'cli_3'

    def __init__(self, client_name):
        self.name = client_name
        self.client_containers = list()

    def __str__(self):
        return f'{self.name:<5} КТК:{len(self):<8} Средний простой: {self.average_containers_time_past():>5}'

    def __len__(self):
        return len(self.client_containers)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            if other.name == self.name:
                return True
            else:
                return False
        elif isinstance(other, str):
            if other == self.name:
                return True
            else:
                return False
        else:
            raise NotImplementedError

    def average_containers_time_past(self):
        days = [client_container.days_past_from_today for client_container in self.client_containers]
        if len(self.client_containers) == 0:
            return '-'
        return round(sum(days) / len(self.client_containers), 2)


class ClientReader:
    def __init__(self, text):
        self.text = text
        self.client_containers = list()
        self.clients = set()

    def process(self):
        self.find_client_containers_rows()
        self.find_unique_clients()
        self.add_client_containers_to_clients()

    def find_client_containers_rows(self):
        for line in self.text.split('\n'):
            cont = Container.find_container_number(line)
            date = re.search(r'\d\d\.\d\d.\d{4}', line)
            client_name = ClientContainer.get_client_name_from_row(line)
            if cont and date:
                row = ClientContainer(cont, date.group(0), client_name)
                self.client_containers.append(row)

    def get_order_clients_list(self):
        li = list(self.clients)
        li.sort(key=lambda client: len(client), reverse=True)
        return li

    def result_json(self):
        clients_data = []
        for client in self.clients:
            dic = {}
            dic['name'] = client.name
            dic['len'] = len(client)
            dic['avg'] = client.average_containers_time_past()
            clients_data.append(dic)
        clients_data.sort(key=lambda client: client['len'], reverse=True)
        return json.dumps(clients_data)

    def find_unique_clients(self):
        for client_container in self.client_containers:
            client = Client(client_container.client_name)
            self.clients.add(client)

    def add_client_containers_to_clients(self):
        for client in self.clients:
            for client_container in self.client_containers:
                if client_container.client_name == client.name:
                    client.client_containers.append(client_container)

    def result_for_textarea(self):
        strings = map(str, self.get_order_clients_list())
        return '\n'.join(strings)

    def __len__(self):
        return len(self.client_containers)
