# Generated by Django 5.1.6 on 2025-03-13 02:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_cartebancaire_cvc_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartebancaire',
            name='cvc',
            field=models.CharField(default='895', max_length=3),
        ),
        migrations.AlterField(
            model_name='cartebancaire',
            name='date_expiration',
            field=models.DateField(default=datetime.date(2027, 3, 13)),
        ),
    ]
