# Generated by Django 5.1.6 on 2025-03-14 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_videoconference_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoconference',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cartebancaire',
            name='cvc',
            field=models.CharField(default='961', max_length=3),
        ),
    ]
