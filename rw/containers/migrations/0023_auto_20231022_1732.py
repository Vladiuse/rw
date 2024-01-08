# Generated by Django 3.2.18 on 2023-10-22 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0022_auto_20230421_2015'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faceproxy',
            options={'ordering': ['-pk'], 'verbose_name': 'Контрагент', 'verbose_name_plural': 'Контрагент'},
        ),
        migrations.AddField(
            model_name='clientuser',
            name='available_clients',
            field=models.ManyToManyField(blank=True, to='containers.ClientUser'),
        ),
        migrations.AlterField(
            model_name='faceproxy',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='faces', related_query_name='face', to='containers.clientuser'),
        ),
    ]
