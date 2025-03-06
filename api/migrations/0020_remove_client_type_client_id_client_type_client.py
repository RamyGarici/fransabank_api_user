# Generated by Django 5.1.6 on 2025-03-06 00:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_alter_typeclient_nom_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='type_client_id',
        ),
        migrations.AddField(
            model_name='client',
            name='type_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.typeclient'),
        ),
    ]
