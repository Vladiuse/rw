import re
from collections import Counter
import json


class NotContainerError(Exception):
    pass


class Container:
    A = 'AAAA1234567'
    B = 'BBBB1234567'
    C = 'CCCC1234567'
    D = 'DDDD1234567'
    F = 'FFFF1234567'
    E = 'EEEE1234567'

    LETTERS_WEIGHT = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19, 'J': 20,
        'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29, 'S': 30, 'T': 31,
        'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38,
    }

    def __init__(self, container_id: str, source_text_line=''):
        self.id = container_id
        self.text_line = source_text_line
        self.date = None

        self.find_date()

    @property
    def json(self):
        return {'id': self.id, 'text_line': self.text_line}

    @staticmethod
    def find_container_number(text_line, pretty=False):
        """Поиск в строке номера контейнера"""
        v_number = re.search('[A-zА-я]{4}\s{0,4}0{0,2}\d{7}', text_line)
        if v_number:
            container = v_number.group(0)
            if pretty:
                container = Container.prettify_container_number(container)
            return container
        return None


    def find_date(self):
        date = re.search(r'\d\d\.\d\d.\d{2,4}', self.text_line)
        if date:
            self.date = date.group(0)



    @staticmethod
    def prettify_container_number(container_number):
        """Уюирает 00 или 0 у номера контейнера и убирает пробелы"""
        container_number = container_number.replace(' ', '')
        container_number = container_number.upper()
        if container_number[4:6] == '00' and len(container_number) == 13:
            container_number = container_number[:4] + container_number[6:]
        if container_number[4:5] == '0' and len(container_number) == 12:
            container_number = container_number[:4] + container_number[5:]
        return container_number

    def is_has_ru_letters(self):
        """Есть ли в номере контейнера русские буквы"""
        return not bool(re.search('[A-z]{4}\d{7}', self.id))

    def is_container_number_correct(self):
        """Явзяеться ли номер контейнера корректным"""
        if self.is_has_ru_letters():
            return False
        res = 0
        if not self.id:
            return False
        for pos, char in enumerate(self.id[:-1]):

            if pos < 4:
                number = Container.LETTERS_WEIGHT[char] * 2 ** pos
            else:
                number = int(char) * 2 ** pos
            res += number

        if self.id[-1] == str(res % 11)[-1]:
            return True
        else:
            return False

    def __hash__(self):
        res = ''
        for char in self.id:
            res += str(ord(char))
        return int(res)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __str__(self):
        return self.id

    def __repr__(self):
        return str({'id': self.id, 'text_line': self.text_line})


class ContainerList:

    def __init__(self, *containers):
        self.containers = list(containers)
        self._validate()

    @staticmethod
    def create_container_list_from_seq(seq):
        """Создсть список с контейнерами из списка со строками (для тестов)"""
        c_list = ContainerList()
        for num in seq:
            c = Container(num)
            c_list.append(c)
        return c_list

    def _validate(self):
        """Все ли контейнеры являються классом Container"""
        if not all([isinstance(item, Container) for item in self.containers]):
            raise NotContainerError

    def append(self, elem: Container):
        """добавить контейнер в список"""
        if not (isinstance(elem, Container)):
            raise NotContainerError
        self.containers.append(elem)

    def __str__(self):
        return f'<ContainerList:len={len(self)}> {self.containers}'

    def __repr__(self):
        return str(self.containers)

    def __len__(self):
        return len(self.containers)

    def __iter__(self):
        self.i = -1
        return self

    def __next__(self):
        self.i += 1
        try:
            return self.containers[self.i]
        except IndexError:
            raise StopIteration

    def __sub__(self, other):
        """Уникальные контейнеры для списка"""
        if not isinstance(other, ContainerList):
            raise NotImplemented
        s1 = set(self.containers)
        s2 = set(other.containers)
        res = s1 - s2
        return ContainerList(*res)

    def __and__(self, other):
        """Общие контейнеры у 2х списков"""
        if not isinstance(other, ContainerList):
            raise NotImplemented
        s1 = set(self.containers)
        s2 = set(other.containers)
        res = s1 & s2
        return ContainerList(*res)

    @property
    def rus_number(self):
        """Контейнеры с русскими буквами"""
        ru_containers = filter(Container.is_has_ru_letters, self.containers)
        return ContainerList(*ru_containers)

    @property
    def unique(self):
        """Уникальные номера контейнеров"""
        unique_containers = set(self.containers)
        return ContainerList(*unique_containers)

    @property
    def duplicates(self):
        """Контейнеры дубли в списке"""
        counter = Counter()
        counter.update(self.containers)
        duplicates_containers = list()
        for k, v in counter.items():
            if v > 1:
                duplicates_containers.append(k)
        return ContainerList(*duplicates_containers)

    @property
    def incorrect_number(self):
        """некорекнтные номера контейнеров"""
        incorrect_number = filter(lambda container: not container.is_container_number_correct(), self.containers)
        return ContainerList(*incorrect_number)

    def json(self):
        """Список в json формате"""
        li = list()
        for con in self.containers:
            li.append(con.json)
        return json.dumps(li)


class ContainerFile:

    def __init__(self, text_file):
        self.text_file = text_file
        for char in '"\'':
            self.text_file = self.text_file.replace(char, '')
        self.containers = ContainerList()
        self.no_containers_lines = []

    def process(self):
        """Отсеять строки с контейнерами и без и наполнить список"""
        for char in '\r', '\t':
            self.text_file = self.text_file.replace(char, '\n')

        for line in self.text_file.split('\n'):
            container_number = Container.find_container_number(line, pretty=True)
            if container_number:
                # container_number = Container.prettify_container_number(container_number)
                container = Container(container_number, source_text_line=line)
                self.containers.append(container)
            else:
                if line != '':
                    self.no_containers_lines.append(line)

    def get_no_containers_lines_json(self):
        """Получить список json строк файла без контейнеров"""
        res = json.dumps(self.no_containers_lines)
        return res


class ContainerReader:

    def __init__(self, file_text_1, file_text_2):
        self.file_1 = ContainerFile(file_text_1)
        self.file_2 = ContainerFile(file_text_2)
        self.file_1.process()
        self.file_2.process()



    def incorrect_1(self):
        """Некоректные номера из файла 1"""
        return self.file_1.containers.incorrect_number.json()

    def incorrect_2(self):
        """Некоректные номера из файла 2"""
        return self.file_2.containers.incorrect_number.json()

    def unique_containers_file_1(self):
        """Уникальные контейнеры для файла 1"""
        return self.file_1.containers - self.file_2.containers

    def unique_containers_file_2(self):
        """Уникальные контейнеры для файла 2"""
        return self.file_2.containers - self.file_1.containers

    def common_containers(self):
        """Общие контейнеры для 2х файлов"""
        return self.file_1.containers & self.file_2.containers


if __name__ == '__main__':
    pass
