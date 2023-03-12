# Generated by Django 3.2.10 on 2023-02-11 09:56

from django.db import migrations, models
import django.db.models.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientContainerRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('container', models.CharField(max_length=11)),
                ('client_name', models.CharField(max_length=30)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ClientDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Имя документа')),
                ('document', models.TextField(verbose_name='Текст документа')),
                ('load_date', models.DateField(default=django.utils.timezone.now)),
                ('document_date', models.DateField(blank=True)),
            ],
        ),
        migrations.DeleteModel(
            name='ClientContainer',
        ),
        migrations.AddField(
            model_name='clientcontainerrow',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.fields.CharField, related_name='rows', related_query_name='row', to='containers.clientdoc'),
        ),
    ]
