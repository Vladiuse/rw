# Generated by Django 3.2.18 on 2023-03-12 16:14

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0006_auto_20230225_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientdoc',
            name='document',
        ),
        migrations.RemoveField(
            model_name='clientdoc',
            name='load_date',
        ),
        migrations.AddField(
            model_name='clientcontainerrow',
            name='area',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(99)]),
        ),
        migrations.AddField(
            model_name='clientdoc',
            name='area_document',
            field=models.FileField(blank=True, upload_to='containers/client_container', verbose_name='Файл с номерами участков'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='client_row_pos',
            field=models.CharField(choices=[('93:109', 'Книга выгрузки'), ('48:75', 'Книга вывоза')], default='93:109', max_length=10, verbose_name='Тип загржаемого файла'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='description',
            field=models.TextField(blank=True, verbose_name='Отписание'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='document_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата документа'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='document_file',
            field=models.FileField(upload_to='containers/client_container', verbose_name='Исходный документ'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='name',
            field=models.CharField(blank=True, default='Без имени', max_length=40, verbose_name='Имя документа'),
        ),
    ]