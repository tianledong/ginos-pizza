# Generated by Django 3.0.8 on 2020-07-11 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20200711_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='one_size',
            field=models.BooleanField(default=False),
        ),
    ]
