# Generated by Django 3.0.7 on 2020-07-10 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinarspa_models', '0003_auto_20200701_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='subetemsilcisi',
            name='ustduzey_hak',
            field=models.BooleanField(default=False),
        ),
    ]
