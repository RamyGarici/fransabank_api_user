# Generated by Django 5.1.6 on 2025-03-14 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_videoconference_deleted_at_alter_cartebancaire_cvc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartebancaire',
            name='cvc',
            field=models.CharField(default='880', max_length=3),
        ),
    ]
