# Generated by Django 4.1.6 on 2023-02-12 15:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0003_auto_20230211_1033'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientdoc',
            options={'ordering': ['-document_date', '-pk']},
        ),
        migrations.AddField(
            model_name='clientdoc',
            name='description',
            field=models.TextField(blank=True, default='Нет описания'),
        ),
        migrations.AlterField(
            model_name='clientcontainerrow',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rows', related_query_name='row', to='containers.clientdoc'),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='document_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='clientdoc',
            name='load_date',
            field=models.DateField(default=django.utils.timezone.now, editable=False),
        ),
    ]
