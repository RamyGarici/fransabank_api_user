from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"







def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):  
        instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)  # Identifiant unique du client
    nom = models.CharField(max_length=50)  # Nom du client
    prenom = models.CharField(max_length=50)  # Prénom du client
    date_naissance = models.DateField()  # Date de naissance du client
    lieu_naissance = models.CharField(max_length=50)  # Lieu de naissance
    adresse = models.CharField(max_length=100)  # Adresse du client
    numero_identite = models.CharField(max_length=20, unique=True)  # Numéro d'identité
    nationalite = models.CharField(max_length=50)  # Nationalité du client
    date_creation = models.DateField(auto_now_add=True)  # Date de création du compte
    email = models.EmailField(unique=True)  # Adresse mail du client
    mot_de_passe = models.CharField(max_length=255)  # Mot de passe du profil du client
    type_client_id = models.IntegerField()  # Identifiant du type de client

    def __str__(self):
        return f"{self.prenom} {self.nom}"


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
    compte_id = models.AutoField(primary_key=True)  # Identifiant unique du compte
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client
    type_compte = models.ForeignKey(TypeCompte, on_delete=models.CASCADE)  # Référence au type de compte
    solde = models.DecimalField(max_digits=10, decimal_places=2)  # Solde actuel du compte
    date_ouverture = models.DateField()  # Date d'ouverture du compte
    statut = models.CharField(max_length=20)  # Statut du compte

    def __str__(self):
        return f"Compte {self.compte_id} - Type: {self.type_compte.nom_type} - Client: {self.client.nom} {self.client.prenom}"

class TypeDocument(models.Model):
    type_document_id = models.AutoField(primary_key=True)  # Identifiant unique du type de document
    nom_type = models.CharField(max_length=50)  # Nom du type de document

    def __str__(self):
        return self.nom_type

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)  # Identifiant unique du document
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client associé au document
    type_document = models.ForeignKey(TypeDocument, on_delete=models.CASCADE)  # Référence au type de document
    chemin_fichier = models.CharField(max_length=255)  # Chemin du fichier stocké
    date_upload = models.DateField()  # Date de téléchargement du document
    statut_verif = models.CharField(max_length=20)  # Statut de vérification

    def __str__(self):
        return f"Document {self.document_id} - Type: {self.type_document.nom_type} - Client: {self.client.nom} {self.client.prenom}"

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


