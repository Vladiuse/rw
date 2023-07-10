import re


class Container8Reader:

    def __init__(self, text_1, text_2):
        self.text_1 = text_1
        self.text_2 = text_2
        self.containers_1 = self.find_containers(self.text_1)
        self.containers_2 = self.find_containers(self.text_2)

    @staticmethod
    def find_containers( text):
        return re.findall(r'\d{8}', text)

    def common_containers(self):
        return set(self.containers_1) & set(self.containers_2)

    def unique_1(self):
        return set(self.containers_1) - set(self.containers_2)

    def unique_2(self):
        return set(self.containers_2) - set(self.containers_1)

    @staticmethod
    def is_conaiter8_number_valid(container_number: str):
        control_sum = 0
        for pos, char in enumerate(container_number[:-1]):
            number = int(char)
            if pos % 2 == 0:
                number *= 2
            if number > 9:
                number = sum([int(char) for char in str(number)])
                control_sum += number
            else:
                control_sum += number
        result = (control_sum // 10 + 1) * 10 - control_sum
        if result == 10:
            result = 0
        return str(result) == container_number[-1]

    def incorrect_1(self):
        func = lambda x: not self.is_conaiter8_number_valid(x)
        return list(filter(func,self.containers_1))

    def incorrect_2(self):
        func = lambda x: not self.is_conaiter8_number_valid(x)
        return list(filter(func,self.containers_2))
