# Generated by Django 3.2.18 on 2023-03-13 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0008_auto_20230313_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='worddoc',
            name='rows_without_data',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
