import random
from string import ascii_letters

def month_text(month_num):
    data = {
        '1': 'января',
        '2': 'декабря',
        '3': 'марта',
        '4': 'апреля',
        '5': 'мая',
        '6': 'июня',
        '7': 'июля',
        '8': 'августа',
        '9': 'сентября',
        '10': 'октября',
        '11': 'ноября',
        '12': 'декабря',
    }
    return data[str(month_num)]

def get_random_file_name(length=10):
    result = ''
    for _ in range(length):
        result += random.choice(ascii_letters)
    return result
