from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.forms import ValidationError
from datetime import datetime
from django.utils import timezone
import secrets

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def soft_delete(self):
        self.deleted_at = datetime.now()
        self.save()

        if hasattr(self, 'profile') and self.profile:
            self.profile.soft_delete()
        if hasattr(self, 'demandes_comptes') and self.demandes_comptes:
            self.demandes_comptes.soft_delete()
        if hasattr(self, 'client_profile') and self.client_profile:
            self.client_profile.soft_delete()
    def delete(self, *args, **kwargs):
        self.soft_delete()

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = datetime.now()
        self.save()
    def delete(self, *args, **kwargs):
        self.soft_delete()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name,  
            last_name=instance.last_name     
        )

def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):  
        instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

User = get_user_model() 
class DemandeCompteBancaire(models.Model):   
    demande_id = models.CharField(max_length=12, unique=True, editable=False, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="demandes_comptes") 
    first_name = models.CharField(max_length=100)  
    last_name = models.CharField(max_length=100)  
    date_of_birth = models.DateField()  
    address = models.TextField()  
    phone_number = models.CharField(max_length=20)  
    numero_identite = models.CharField(max_length=20, unique=True)  
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'En attente'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)  
    deleted_at = models.DateTimeField(null=True, blank=True)

    def generate_unique_demande_id(self):
        while True:
            demande_id = str(secrets.randbelow(10**12)).zfill(12)
            if not DemandeCompteBancaire.objects.filter(demande_id=demande_id).exists():
                return demande_id

    def save(self, *args, **kwargs):
        if not self.demande_id:
            self.demande_id = self.generate_unique_demande_id()
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.deleted_at = datetime.now()
        self.save()
        if hasattr(self, 'client') and self.client:
            self.client.soft_delete()
    def delete(self, *args, **kwargs):
        self.soft_delete()

    def __str__(self):
        return f"Demande de {self.user.email if self.user else 'Inconnu'} - {self.status}"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="client_profile") 
    client_id = models.CharField(max_length=16, unique=True, editable=False, blank=True, null=True)
    demande = models.ForeignKey(DemandeCompteBancaire, on_delete=models.SET_NULL, null=True, blank=True, related_name="client")  
    nom = models.CharField(max_length=50)  
    prenom = models.CharField(max_length=50)  
    date_naissance = models.DateField()  
    lieu_naissance = models.CharField(max_length=50, blank=True, null=True) 
    adresse = models.CharField(max_length=100)  
    numero_identite = models.CharField(max_length=20, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    email = models.EmailField(unique=True)  
    type_client_id = models.IntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def generate_unique_id(self):
        while True:
            client_id = str(secrets.randbelow(10**16)).zfill(16)
            if not Client.objects.filter(client_id=client_id).exists():
                return client_id

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = self.generate_unique_id()
        super().save(*args, **kwargs)  

    def soft_delete(self):
        self.deleted_at = datetime.now()
        self.save()
    def delete(self, *args, **kwargs):
        self.soft_delete()

    def __str__(self):
        return f"{self.prenom} {self.nom}"

def create_client(sender, instance, **kwargs):
    if instance.status == 'approved' and not Client.objects.filter(user=instance.user).exists():
        Client.objects.create(
            user=instance.user,
            demande=instance,
            nom=instance.last_name,
            prenom=instance.first_name,
            date_naissance=instance.date_of_birth,
            adresse=instance.address,
            numero_identite=instance.numero_identite,
            email=instance.user.email,
            type_client_id=1  
        )

post_save.connect(create_client, sender=DemandeCompteBancaire)












class TypeClient(models.Model):
    type_client_id = models.AutoField(primary_key=True)  # Identifiant du type
    nom_type = models.CharField(max_length=50)  # Nom du type

    def __str__(self):
        return self.nom_type

class TypeCompte(models.Model):
    type_compte_id = models.AutoField(primary_key=True)  # Identifiant unique du type de compte
    nom_type = models.CharField(max_length=50)  # Nom du type de compte

    def __str__(self):
        return self.nom_type 


class Compte(models.Model): 
    # modele pas utile on peut tout mettre dans client
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client
    type_compte = models.ForeignKey(TypeCompte, on_delete=models.CASCADE)  # Référence au type de compte
    solde = models.DecimalField(max_digits=10, decimal_places=2)  # Solde actuel du compte
    date_ouverture = models.DateField()  # Date d'ouverture du compte
    statut = models.CharField(max_length=20)  # Statut du compte
    deleted_at=models.DateTimeField(null=True,blank=True)

    def soft_delete(self):
        self.deleted_at=datetime.now()
        self.save()

    def __str__(self):
        return f"Compte {self.compte_id} - Type: {self.type_compte.nom_type} - Client: {self.client.nom} {self.client.prenom}"

class TypeDocument(models.Model):
    type_document_id = models.AutoField(primary_key=True)  # Identifiant unique du type de document
    nom_type = models.CharField(max_length=50)  # Nom du type de document

    def __str__(self):
        return self.nom_type

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)  # Identifiant unique du document
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Référence au user associé au document
    #ajout de profil pas besoin on a user
    demande = models.ForeignKey(DemandeCompteBancaire, on_delete=models.CASCADE, blank=True, null=True)
    type_document = models.ForeignKey(TypeDocument, on_delete=models.CASCADE)  # Référence au type de document
    fichier = models.FileField(upload_to='documents/')  # Chemin du fichier stocké
    date_upload = datetime.now()  # Date de téléchargement du document
    statut_verif = models.CharField(max_length=20)  # Statut de vérification
    demande = models.ForeignKey(DemandeCompteBancaire, on_delete=models.CASCADE, blank=True, null=True) #hna bash ndiro relation demandecreation ou document
    deleted_at=models.DateTimeField(null=True,blank=True)

    def soft_delete(self):
        self.deleted_at=datetime.now()
        self.save()


    def __str__(self):
        return f"Document {self.document_id} - Type: {self.type_document.nom_type} - "










class TypeAgent(models.Model):
    type_agent_id = models.AutoField(primary_key=True)  # Identifiant unique du type d'agent
    nom_type = models.CharField(max_length=50)  # Nom du type d'agent

    def __str__(self):
        return self.nom_type

class Agent(models.Model):
    agent_id = models.AutoField(primary_key=True)  # Identifiant unique de l'agent
    nom = models.CharField(max_length=50)  # Nom de l'agent
    prenom = models.CharField(max_length=50)  # Prénom de l'agent
    email = models.EmailField(max_length=100, unique=True)  # Adresse e-mail de l'agent
    role = models.CharField(max_length=50)  # Rôle de l'agent
    type_agent = models.ForeignKey(TypeAgent, on_delete=models.CASCADE)  # Référence au type d'agent

    def __str__(self):
        return f"Agent {self.prenom} {self.nom} - Rôle: {self.role} - Type: {self.type_agent.nom_type}"

class TypeOffre(models.Model):
    type_offre_id = models.AutoField(primary_key=True)  # Identifiant unique du type d'offre
    nom_type = models.CharField(max_length=50)  # Nom du type d'offre

    def __str__(self):
        return self.nom_type

class Offre(models.Model):
    offre_id = models.AutoField(primary_key=True)  # Identifiant unique de l'offre
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client concerné
    type_offre = models.ForeignKey(TypeOffre, on_delete=models.CASCADE)  # Référence au type d'offre
    date_proposition = models.DateField()  # Date de proposition de l'offre
    type_client = models.ForeignKey(TypeClient, on_delete=models.CASCADE)  # Référence au type de client

    def __str__(self):
        return f"Offre {self.offre_id} - Type: {self.type_offre.nom_type} - Client: {self.client.nom} {self.client.prenom}"



class CreditBancaire(models.Model):
    credit_id = models.AutoField(primary_key=True)  # Identifiant unique du crédit
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client concerné
    montant_credite = models.IntegerField()  # Montant du prêt
    taux_interet = models.IntegerField()  # Taux d'intérêt
    date_debut = models.DateField()  # Date de début du prêt
    date_fin = models.DateField()  # Date de fin du prêt
    statut_credit = models.CharField(max_length=50)  # Statut du crédit
    penalite = models.IntegerField()  # Pénalité
    solde_restant = models.IntegerField()  # Solde restant

    def __str__(self):
        return f"Crédit {self.credit_id} - Client: {self.client.nom} {self.client.prenom} - Montant: {self.montant_credite}"


class Echeance(models.Model):
    echeance_id = models.AutoField(primary_key=True)  # Identifiant unique de l'échéance
    credit = models.ForeignKey(CreditBancaire, on_delete=models.CASCADE)  # Référence au crédit concerné
    date_echeance = models.DateField()  # Date de l'échéance
    montant_echeance = models.IntegerField()  # Montant à rembourser à chaque échéance
    statut_echeance = models.CharField(max_length=50)  # Statut de l'échéance

    def __str__(self):
        return f"Échéance {self.echeance_id} - Crédit ID: {self.credit.credit_id} - Montant: {self.montant_echeance}"

class TypeTransaction(models.Model):
    type_transaction_id = models.AutoField(primary_key=True)  # Identifiant unique du type de transaction
    nom_type = models.CharField(max_length=50)  # Nom du type de transaction

    def __str__(self):
        return self.nom_type


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)  # Identifiant unique de la transaction
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)  # Référence au compte
    type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)  # Référence au type de transaction
    montant = models.IntegerField()  # Montant de la transaction (minimum 500 DA)
    date_transaction = models.DateTimeField(auto_now_add=True)  # Date et heure de la transaction
    statut_transaction = models.CharField(max_length=50)  # Statut de la transaction (réussie, échouée)

    def clean(self):
        if self.montant < 500:
            raise ValidationError('Le montant doit être d\'au moins 500 DA.')

    def __str__(self):
        return f"Transaction {self.transaction_id} - Compte ID: {self.compte.compte_id} - Montant: {self.montant} - Statut: {self.statut_transaction}"
        

class ActionNFC(models.Model):
    log_id = models.AutoField(primary_key=True)  # Identifiant unique de l'action
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client concerné
    date_lecture = models.DateTimeField()  # Date et heure de la lecture NFC
    statut_lecture = models.CharField(max_length=20)  # Statut de la lecture

    def __str__(self):
        return f"Action NFC {self.log_id} - {self.statut_lecture} - {self.client.nom} {self.client.prenom}"


class ResultatIA(models.Model):
    resultat_id = models.AutoField(primary_key=True)  # Identifiant unique du résultat
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client concerné
    type_analyse = models.CharField(max_length=50)  # Type d'analyse
    resultat = models.CharField(max_length=50)  # Résultat de l'analyse
    date_analyse = models.DateField()  # Date de l'analyse

    def __str__(self):
        return f"Analyse {self.resultat_id} - {self.type_analyse} - {self.resultat} - {self.client.nom} {self.client.prenom}"


