# Generated by Django 2.1 on 2018-10-05 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0019_auto_20181005_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='de',
            name='loai_de',
        ),
        migrations.AddField(
            model_name='cauhoi',
            name='dung_lam',
            field=models.CharField(default='thi', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='de',
            name='dung_lam',
            field=models.CharField(default='thi', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='de',
            name='thoi_gian',
            field=models.IntegerField(null=True),
        ),
    ]
