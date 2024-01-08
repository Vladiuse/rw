# Generated by Django 3.2.18 on 2023-03-13 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0009_worddoc_rows_without_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaDocFile',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('containers.worddoc',),
        ),
        migrations.CreateModel(
            name='ClientDocFile',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('containers.worddoc',),
        ),
        migrations.RemoveField(
            model_name='clientdoc',
            name='area_document',
        ),
        migrations.RemoveField(
            model_name='clientdoc',
            name='document_file',
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='client_row_pos',
            field=models.CharField(choices=[('Книга выгрузки', 'Книга выгрузки'), ('Книга вывоза', 'Книга вывоза')], default='93:109', max_length=20, verbose_name='Тип загржаемого файла'),
        ),
        migrations.AlterField(
            model_name='worddoc',
            name='rows_without_data',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='clientdoc',
            name='area_doc',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='area_doc', to='containers.areadocfile', verbose_name='Файл с номерами участков'),
        ),
        migrations.AddField(
            model_name='clientdoc',
            name='client_container_doc',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_container_doc', to='containers.clientdocfile'),
        ),
    ]