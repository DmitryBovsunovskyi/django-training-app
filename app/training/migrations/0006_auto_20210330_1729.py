# Generated by Django 3.1.7 on 2021-03-30 17:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_auto_20210330_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='date',
            field=models.DateField(default=datetime.date(2021, 3, 30)),
        ),
    ]