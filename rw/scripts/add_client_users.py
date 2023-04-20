from containers.models import ClientUser
from django.contrib.auth.models import User

data = [
    {
        'username': 'client_1',
        'name': 'ООО АЛЕКСВИТ ЛТ',
    },
    {
        'username': 'client_2',
        'name': 'ОАО "ГОМЕЛЬСКИЙ',
    },
    {
        'username': 'client_3',
        'name': 'СООО "МИДЕА-ГОР',
    },
]

for item in data:
    user = User.objects.create_user(username=item['username'], password='0099')
    ClientUser.objects.create(user=user, client_name=item['name'],client_filter=item['name'])