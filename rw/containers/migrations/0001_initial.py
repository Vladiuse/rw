# Generated by Django 3.2.10 on 2023-01-14 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClientContainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('container', models.CharField(max_length=11)),
                ('client_name', models.CharField(max_length=30)),
                ('date', models.DateField()),
            ],
        ),
    ]
