# Generated by Django 3.2.18 on 2023-03-14 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0012_worddoc_rows_without_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worddoc',
            name='rows_without_data',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]
