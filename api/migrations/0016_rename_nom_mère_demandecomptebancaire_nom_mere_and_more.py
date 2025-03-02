# Generated by Django 5.1.6 on 2025-03-02 11:32

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_statut_demandecomptebancaire_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='demandecomptebancaire',
            old_name='Nom_mère',
            new_name='Nom_mere',
        ),
        migrations.RenameField(
            model_name='demandecomptebancaire',
            old_name='Prénom_mère',
            new_name='Prénom_mere',
        ),
        migrations.RenameField(
            model_name='demandecomptebancaire',
            old_name='Prénom_père',
            new_name='Prénom_pere',
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='Nationalité2',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='fatca_TIN',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='fatca_greencardAM',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='fatca_nationalitéAM',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='fatca_residenceAM',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='fonction',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='lieu_denaissance',
            field=models.CharField(default='Non Renseigné', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='nom_employeur',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='demandecomptebancaire',
            name='nom_jeunefille',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification_token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='ActionNFC',
        ),
    ]
