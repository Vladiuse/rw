import re


class Vagon:
    LETTERS_WEIGHT = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19, 'J': 20,
        'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29, 'S': 30, 'T': 31,
        'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38,
    }

    def __init__(self, vagon_data):
        self.vagon_data = vagon_data + '\n'
        self.id = self.find_vagon()

    def __str__(self):
        return str(self.id + '\n')



    @staticmethod
    def find_vagon_number(text_line):
        v_number =re.search('[A-zА-я]{4}\s{0,4}0{0,2}\d{7}', text_line)
        if v_number:
            return v_number.group(0)
        return None

    @staticmethod
    def prettify_vagon_number(vagon_number):
        """Уюирает 00 или 0 у номера контейнера и убирает пробелы"""
        vagon_number = vagon_number.replace(' ', '')
        vagon_number = vagon_number.upper()
        if vagon_number[4:6] == '00' and len(vagon_number) == 13:
            vagon_number = vagon_number[:4] + vagon_number[6:]
        if vagon_number[4:5] == '0' and len(vagon_number) == 12:
            vagon_number = vagon_number[:4] + vagon_number[5:]
        return vagon_number



    def find_vagon(self):
        vagon = re.search('[A-zА-я]{4}\s{0,2}0{0,2}\d{7}', self.vagon_data)
        if vagon:
            vagon_id = vagon.group(0)
            vagon_id = vagon_id.replace(' ', '')
            vagon_id = vagon_id.replace('\t', '')
            if len(vagon_id) == 13:
                vagon_id = vagon_id[:4] + vagon_id[6:]
            return vagon_id.upper()

    def is_vagon_number_correct(self):
        if self.is_has_ru_letters():
            return False
        res = 0
        if not self.id:
            return None
        for id, char in enumerate(self.id[:-1]):

            if id <4:
                number = Vagon.LETTERS_WEIGHT[char] * 2**id
                print(id,char,Vagon.LETTERS_WEIGHT[char], 2**id)
            else:
                number = int(char) * 2**id
                print(id,char, 2**id)
            res += number

        if self.id[-1] == str(res%11)[-1]:
            return True
        else:
            return False

    def is_has_ru_letters(self):
        return not bool(re.search('[A-z]{4}\d{7}', self.id))

    def get_ru_warning_id(self):
        symbols = 'qwertyuiopasdfghjklzxcvbnm'.upper()
        war_id = ''
        for char in self.id[:4]:
            if char not in symbols:
                war_id += f'<span>{char}</span>'
            else:
                war_id += char
        war_id += self.id[4:]
        return war_id + '\n'


class VagReader:

    def __init__(self, text):
        self.text = text
        self.vagons = []
        self.no_vagons_rows = []
        self.process()

    def process(self):
        for row in self.text.split('\n'):
            row = row.strip()
            vagon = Vagon(row)
            if vagon.id:
                self.vagons.append(vagon)
            else:
                self.no_vagons_rows.append(row)

    def get_no_vagon_rows(self) -> str:
        return '\n'.join(self.no_vagons_rows)

    def get_vagons_ids(self) -> set:
        """Получить все айди вагонов"""
        return set(vagon.id for vagon in self.vagons)

    def get_vagons_by_ids(self, ids):
        """отфильтровать вагоны по айди"""
        return filter(lambda vagon: vagon.id in ids, self.vagons)

    def sort_vagons(self, vagons: list) -> list:
        return sorted(vagons, key=lambda vagon: (vagon.id[:4], vagon.id[4:]))

    def rus_vagons(self):
        return list(filter(lambda vagon: vagon.is_has_ru_letters(), self.vagons))

    def get_incorrect_vagons(self):
        return list(filter(lambda vagon: not vagon.is_container_number_correct(), self.vagons))

    def __sub__(self, instance):
        unigue_ids = self.get_vagons_ids() - instance.get_vagons_ids()
        unique_vagons = list(self.get_vagons_by_ids(unigue_ids))
        return list(self.sort_vagons(unique_vagons))

    def __and__(self, instance):
        jeneral_ids = self.get_vagons_ids() & instance.get_vagons_ids()
        jeneral_vagons = list(self.get_vagons_by_ids(jeneral_ids))
        return list(self.sort_vagons(jeneral_vagons))





if __name__ == '__main__':
    row = 'TCLU2261070'
    vag = Vagon(row)
    print(vag.is_vagon_number_correct())
