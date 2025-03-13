# Generated by Django 5.1.6 on 2025-03-13 16:11

import api.models
import datetime
import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeAgent',
            fields=[
                ('type_agent_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TypeClient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeCompte',
            fields=[
                ('type_compte_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TypeDocument',
            fields=[
                ('type_document_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeOffre',
            fields=[
                ('type_offre_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TypeTransaction',
            fields=[
                ('type_transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.CharField(blank=True, editable=False, max_length=16, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('date_naissance', models.DateField()),
                ('lieu_naissance', models.CharField(blank=True, max_length=50, null=True)),
                ('adresse', models.CharField(max_length=100)),
                ('numero_identite', models.CharField(max_length=20, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('type_client_id', models.IntegerField(default=1)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('solde', models.DecimalField(decimal_places=2, max_digits=15)),
                ('password_client', models.CharField(blank=True, max_length=128, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Compte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solde', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_ouverture', models.DateField()),
                ('statut', models.CharField(max_length=20)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('type_compte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typecompte')),
            ],
        ),
        migrations.CreateModel(
            name='CreditBancaire',
            fields=[
                ('credit_id', models.AutoField(primary_key=True, serialize=False)),
                ('montant_credite', models.IntegerField()),
                ('taux_interet', models.IntegerField()),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('statut_credit', models.CharField(max_length=50)),
                ('penalite', models.IntegerField()),
                ('solde_restant', models.IntegerField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
            ],
        ),
        migrations.CreateModel(
            name='DemandeCompteBancaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('demande_id', models.CharField(blank=True, editable=False, max_length=12, null=True, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('nom_jeunefille', models.CharField(blank=True, max_length=100, null=True)),
                ('lieu_denaissance', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('address', models.TextField()),
                ('phone_number', models.CharField(max_length=20)),
                ('numero_identite', models.CharField(max_length=20, unique=True)),
                ('Pays_naissance', models.CharField(max_length=20)),
                ('Nationalité', models.CharField(max_length=20)),
                ('Nationalité2', models.CharField(blank=True, max_length=20, null=True)),
                ('Prénom_pere', models.CharField(max_length=20)),
                ('Nom_mere', models.CharField(max_length=20)),
                ('Prénom_mere', models.CharField(max_length=20)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photo/')),
                ('signature', models.ImageField(blank=True, null=True, upload_to='signatures/')),
                ('civilité', models.CharField(choices=[('Mr', 'Monsieur'), ('Mme', 'Madame')], max_length=5)),
                ('situation_familliale', models.CharField(choices=[('Célibataire', 'Célibataire'), ('Marié(e)', 'Marié(e)'), ('Divorcé(e)', 'Divorcé(e)'), ('Veuf/veuve', 'Veuf/veuve')], max_length=15)),
                ('fonction', models.CharField(blank=True, max_length=30, null=True)),
                ('nom_employeur', models.CharField(blank=True, max_length=100, null=True)),
                ('fatca_nationalitéAM', models.BooleanField(default=False)),
                ('fatca_residenceAM', models.BooleanField(default=False)),
                ('fatca_greencardAM', models.BooleanField(default=False)),
                ('fatca_TIN', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_comptes', to=settings.AUTH_USER_MODEL)),
                ('type_client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.typeclient')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='demande',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', to='api.demandecomptebancaire'),
        ),
        migrations.CreateModel(
            name='Echeance',
            fields=[
                ('echeance_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_echeance', models.DateField()),
                ('montant_echeance', models.IntegerField()),
                ('statut_echeance', models.CharField(max_length=50)),
                ('credit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.creditbancaire')),
            ],
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('role', models.CharField(choices=[('agent', 'Agent Bancaire'), ('admin', 'Administrateur')], default='agent', max_length=10)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('emp_id', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False, unique=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employe_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResultatIA',
            fields=[
                ('resultat_id', models.AutoField(primary_key=True, serialize=False)),
                ('type_analyse', models.CharField(max_length=50)),
                ('resultat', models.CharField(max_length=50)),
                ('date_analyse', models.DateField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('agent_id', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('role', models.CharField(max_length=50)),
                ('type_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typeagent')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('document_id', models.AutoField(primary_key=True, serialize=False)),
                ('fichier', models.FileField(upload_to='documents/')),
                ('statut_verif', models.CharField(choices=[('not verified', 'non vérifié'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], default='not verified', max_length=15)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('demande', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.demandecomptebancaire')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('type_document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typedocument')),
            ],
        ),
        migrations.CreateModel(
            name='Offre',
            fields=[
                ('offre_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_proposition', models.DateField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('type_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typeclient')),
                ('type_offre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typeoffre')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('montant', models.IntegerField()),
                ('date_transaction', models.DateTimeField(auto_now_add=True)),
                ('statut_transaction', models.CharField(max_length=50)),
                ('compte', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.compte')),
                ('type_transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.typetransaction')),
            ],
        ),
        migrations.CreateModel(
            name='cartebancaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_carte', models.CharField(default=api.models.generate_numero_carte, editable=False, max_length=16, unique=True)),
                ('date_ouverture', models.DateField(default=django.utils.timezone.now)),
                ('date_expiration', models.DateField(default=datetime.date(2027, 3, 13))),
                ('cvc', models.CharField(default='135', max_length=3)),
                ('type_carte', models.CharField(choices=[('VISA', 'Visa'), ('MASTERCARD', 'MasterCard'), ('VISA_PLATINUM', 'Visa Platinum'), ('MASTERCARD_ELITE', 'MasterCard World Elite'), ('AMEX', 'American Express'), ('AMEX_GOLD', 'American Express Gold')], default='VISA', max_length=20)),
                ('statut_carte', models.CharField(choices=[('active', 'Active'), ('expirée', 'Expirée'), ('bloquée', 'Bloquée')], default='active', max_length=20)),
                ('plafond_paiement', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), max_digits=10)),
                ('plafond_retrait', models.DecimalField(decimal_places=2, default=Decimal('2000.00'), max_digits=10)),
                ('frais_carte', models.DecimalField(decimal_places=2, default=Decimal('50.00'), max_digits=6)),
                ('is_active', models.BooleanField(default=True)),
                ('frais_payes', models.BooleanField(default=False)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('client_id', 'type_carte'), name='unique_carte_par_type_par_client')],
            },
        ),
        migrations.CreateModel(
            name='VideoConference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_url', models.TextField(blank=True, null=True)),
                ('scheduled_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('done', 'Terminée'), ('canceled', 'Annulée')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conferences_client', to='api.client')),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conferences_employe', to='api.employe')),
            ],
            options={
                'unique_together': {('client', 'employe', 'status')},
            },
        ),
    ]
