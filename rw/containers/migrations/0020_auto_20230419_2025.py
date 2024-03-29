# Generated by Django 3.2.18 on 2023-04-19 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0019_auto_20230417_1953'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceProxy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('attorney', models.CharField(max_length=30)),
            ],
        ),
        migrations.RemoveField(
            model_name='clientsreport',
            name='area_doc',
        ),
        migrations.AlterField(
            model_name='clientsreport',
            name='clients',
            field=models.ManyToManyField(blank=True, related_name='reports', related_query_name='report', to='containers.ClientUser'),
        ),
        migrations.DeleteModel(
            name='AreaDocFile',
        ),
    ]
