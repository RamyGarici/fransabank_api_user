# Generated by Django 5.1.6 on 2025-02-22 15:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_compte_document_remove_compte_nom_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='demande',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', to='api.demandecomptebancaire'),
        ),
        migrations.AlterField(
            model_name='demandecomptebancaire',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='demandes_comptes', to=settings.AUTH_USER_MODEL),
        ),
    ]
