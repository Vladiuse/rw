from containers.models import WordDoc,ClientsReport
import os

WordDoc.objects.all().delete()
ClientsReport.objects.all().delete()

containers_files_path = '/home/vlad/PycharmProjects/rw/rw/media'
for file in os.listdir(containers_files_path):
    os.remove(os.path.join(containers_files_path, file))