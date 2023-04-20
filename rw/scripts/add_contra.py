from containers.models import FaceProxy
data = [
    {
        'name': 'Леонович А.А.',
        'attorney': '86-22 от 29.07.2022'
    },
    {
        'name': 'Крупенько К.С.',
        'attorney': '85-22 от 05.07.2022'
    },
    {
        'name': 'Пользователь 3',
        'attorney': '300 от 15,02,2023'
    },
]
faces_to_create = []
for item in data:
    f = FaceProxy(name=item['name'], attorney=item['attorney'])
    faces_to_create.append(f)

FaceProxy.objects.bulk_create(faces_to_create)