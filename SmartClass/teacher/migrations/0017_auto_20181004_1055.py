# Generated by Django 2.1 on 2018-10-04 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0016_khoa_nienkhoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nienkhoa',
            name='nam_hoc',
            field=models.IntegerField(),
        ),
    ]
