# Generated by Django 5.1.6 on 2025-02-28 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_date_creation_client_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='demandecomptebancaire',
            old_name='status',
            new_name='statut',
        ),
    ]
