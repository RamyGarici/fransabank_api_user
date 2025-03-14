from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.forms import ValidationError
from datetime import datetime,timedelta
from django.db.models import  UniqueConstraint,Q
from django.utils.timezone import now
from django.utils import timezone
import secrets
import uuid
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied
import random
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from django.utils.timezone import make_aware, get_current_timezone
from .constants import PLAFONDS_CARTES

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    def is_deleted(self):
        """Retourne True si l'utilisateur est soft deleted"""
        return self.deleted_at is not None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def soft_delete(self):
     self.deleted_at = timezone.now()
     self.save()

     # Assurez-vous que vous avez bien une instance de profile et d'employe
     if hasattr(self, 'profile') and self.profile:
        self.profile.soft_delete()
     if hasattr(self, 'demandes_comptes_profile') and self.demandes_comptes:
        self.demandes_comptes_profil.soft_delete()
     if hasattr(self, 'client_profile'):
       for client in self.client_profile.all():  # Boucle sur tous les profils clients liés
        client.soft_delete()
     # Vérifiez si `self.employe` est bien une instance de `Employe`
     if hasattr(self, 'employe_profile') and self.employe_profile:
        self.employe_profile.soft_delete()  # Cela devrait maintenant fonctionner


    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
        self.soft_delete()
    def __str__(self):
        return self.username
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and not request.user.is_superuser:
            admin_class = EmployeAdmin(self.__class__, admin.site)  # Obtenir l'admin associé
            if not admin_class.has_delete_permission(request, self):
                raise PermissionDenied("❌ Vous n'avez pas la permission de supprimer cet employé.")
        self.soft_delete()
        if hasattr(self, "user") and self.user:
         self.user.deleted_at = now()  # Marquer l'utilisateur comme supprimé
         self.user.save(update_fields=["deleted_at"])  # Sauvegarder uniquement ce champ

  

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

class TypeClient(models.Model):  
  TYPE_CHOICES = [
        (1, 'Étudiant'),
        (2, 'Commerçant'),
        (3, 'Professionnel'),
        (4, 'Personnel'),
        (5, 'Jeune/Enfant'),
    ]
  id = models.AutoField(primary_key=True) 
  nom_type = models.CharField(max_length=50, unique=True)

  def __str__(self):
        return self.nom_type
  



class DemandeCompteBancaire(models.Model):   
    demande_id = models.CharField(max_length=12, unique=True, editable=False, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="demandes_comptes")
    first_name = models.CharField(max_length=100)  
    last_name = models.CharField(max_length=100) 
    nom_jeunefille = models.CharField(max_length=100 , blank=True,null=True)
    lieu_denaissance=models.CharField(max_length=100) 
    date_of_birth = models.DateField()  
    address = models.TextField()  #
    phone_number = models.CharField(max_length=20)  
    numero_identite = models.CharField(max_length=20, unique=True) 
    Pays_naissance= models.CharField(max_length=20) # 
    Nationalité= models.CharField(max_length=20)
    Nationalité2= models.CharField(max_length=20,blank=True,null=True)
    Prénom_pere=models.CharField(max_length=20)
    Nom_mere= models.CharField(max_length=20)
    Prénom_mere = models.CharField(max_length=20)
    
    photo = models.ImageField(upload_to='photo/',blank=True,null=True) #
    signature = models.ImageField(upload_to='signatures/',blank=True,null=True) #
    CIVILITE_CHOICES = [
        ('Mr', 'Monsieur'),
        ('Mme', 'Madame'),
    ]

    SITUATION_FAMILIALE_CHOICES = [
        ('Célibataire', 'Célibataire'),
        ('Marié(e)', 'Marié(e)'),
        ('Divorcé(e)', 'Divorcé(e)'),
        ('Veuf/veuve', 'Veuf/veuve'),
    ]

    civilité = models.CharField(max_length=5, choices=CIVILITE_CHOICES)
    situation_familliale = models.CharField(max_length=15, choices=SITUATION_FAMILIALE_CHOICES)

    fonction = models.CharField(max_length=30 , null=True , blank = True)
    nom_employeur = models.CharField(max_length=100 ,null=True,blank=True) #
    type_client = models.ForeignKey(TypeClient, on_delete=models.SET_NULL, null=True, blank=True) #


    #fatca natio américaine
    fatca_nationalitéAM = models.BooleanField(default=False)
    fatca_residenceAM = models.BooleanField(default=False)
    fatca_greencardAM = models.BooleanField(default=False)
    fatca_TIN = models.CharField(max_length=20,null=True,blank=True)

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

    def clean(self):
        if self.Nationalité and self.Nationalité.lower() == "américaine" or (self.Nationalité2 and self.Nationalité2.lower() == "américaine"):

            if not (self.fatca_nationalitéAM or self.fatca_greencardAM or self.fatca_residenceAM or self.fatca_TIN):
                raise ValidationError("information fatca doivent etre remplis") 
       
    def save(self, *args, **kwargs):
        if not self.demande_id:
            self.demande_id = self.generate_unique_demande_id()
        self.clean()
        super().save(*args, **kwargs)


    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
        if hasattr(self, 'document_set'):
         for document in self.document_set.all():
            document.soft_delete()

        if hasattr(self, 'client') and self.client:
            self.client.soft_delete()
    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
        self.soft_delete()

    def __str__(self):
        return f"Demande de {self.user.email if self.user else 'Inconnu'} - {self.status}"

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="client_profile") 
    client_id = models.CharField(primary_key=True, max_length=16, unique=True, editable=False, blank=True)  # Utilisation correcte pour une valeur générée
    demande = models.ForeignKey('DemandeCompteBancaire', on_delete=models.SET_NULL, null=True, blank=True, related_name="client")  
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
    solde = models.DecimalField(max_digits=15, decimal_places=2,null=False,default=1)
  
    password_client = models.CharField(max_length=128, blank=True, null=True)

    def set_password_client(self, raw_password):
      
        self.password_client = make_password(raw_password)

    def check_password_client(self, raw_password):
       
        return check_password(raw_password, self.password_client)

    def generate_unique_id(self):
        while True:
            client_id = str(secrets.randbelow(10**16)).zfill(16)  # Assurer 16 chiffres
            if not Client.objects.filter(client_id=client_id).exists():
                return client_id
    
    def get_cartes(self):
        
        return self.cartebancaire_set.all()


    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = self.generate_unique_id()
        super().save(*args, **kwargs)  
        if not self.password_client and self.user and self.user.password:
            self.password_client = self.user.password
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
        if hasattr(self, 'compte_set'):
         for compte in self.compte_set.all():
            compte.soft_delete()
        if hasattr(self, "conferences_client"):
         for conference in self.conferences_client.all():
            conference.soft_delete()
    

    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
        self.soft_delete()
        if hasattr(self, "user") and self.user:
          self.user.deleted_at = now()  # Marquer l'utilisateur comme supprimé
          self.user.save(update_fields=["deleted_at"])  # Sauvegarder uniquement ce champ
         

    def restore(self):
     """Restaure un client et ses vidéoconférences associées"""
     self.deleted_at = None
     self.save()


     if hasattr(self, "conferences_client"):
        for conference in self.conferences_client.all():
            conference.deleted_at = None
            conference.save()

   
     if hasattr(self, "compte_set"):
        for compte in self.compte_set.all():
            compte.deleted_at = None
            compte.save()


     if hasattr(self, "user") and self.user:
        self.user.deleted_at = None
        self.user.save(update_fields=["deleted_at"])

        
      

    
        
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"

def create_client(sender, instance, **kwargs):
    if instance.status == 'approved' and not Client.objects.filter(user=instance.user).exists():
        # Créer un nouveau client avec les données de la demande
        client = Client.objects.create(
            client_id=Client().generate_unique_id(),  # Générer un ID unique pour le client
            user=instance.user,
            demande=instance,
            nom=instance.last_name,
            prenom=instance.first_name,
            date_naissance=instance.date_of_birth,
            adresse=instance.address,
            numero_identite=instance.numero_identite,
            email=instance.user.email,
            type_client_id=1,
        )
        
        # Assigner le mot de passe du client à partir de l'utilisateur
        if instance.user.password:
            client.set_password_client(instance.user.password)  # Utilise la méthode pour hacher le mot de passe
            client.save()
post_save.connect(create_client, sender=DemandeCompteBancaire)

def generate_numero_carte():
    return f"213{''.join(str(random.randint(0, 9)) for _ in range(13))}"

def default_expiration_date():
    return timezone.now().date() + timedelta(days=2*365)

def generate_cvc():
    return str(random.randint(100, 999))

class cartebancaire(models.Model):
    client_id= models.ForeignKey(Client ,  on_delete=models.CASCADE)
    numero_carte = models.CharField(max_length=16, unique=True , default=generate_numero_carte , editable=False)
    date_ouverture = models.DateField(default=timezone.now)
    date_expiration =models.DateField(default=default_expiration_date()) 
    cvc =  models.CharField(max_length=3,default=generate_cvc() )
    TYPE_CARTE_CHOICES = [
        ("VISA", "Visa"),
        ("MASTERCARD", "MasterCard"),
        ("VISA_PLATINUM", "Visa Platinum"),
        ("MASTERCARD_ELITE", "MasterCard World Elite"),
        ("AMEX", "American Express"),
        ("AMEX_GOLD", "American Express Gold"),
    ]
    type_carte = models.CharField(max_length=20, choices=TYPE_CARTE_CHOICES, default="VISA")
    STATUT_CARTE_CHOICES = [
    ("active", "Active"),
    ("expirée", "Expirée"),
    ("bloquée", "Bloquée"),
]
    statut_carte = models.CharField(max_length=20,choices=STATUT_CARTE_CHOICES, default="active")
    plafond_paiement = models.DecimalField(max_digits=10, decimal_places=2,default=Decimal("5000.00"))  
    plafond_retrait = models.DecimalField(max_digits=10, decimal_places=2,default=Decimal("2000.00"))
    frais_carte = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("50.00"))
    is_active = models.BooleanField(default=True)#pour desactiver une carte
    frais_payes = models.BooleanField(default=False)


    def payer_frais(self):
        self.frais_payes = True
        self.save()
    
    def est_expiree(self):
        return timezone.now().date() > self.date_expiration
    
    def renouveler_carte(self):
        if not self.est_expiree():
            raise ValueError("La carte n'est pas encore expirée.")

        if self.client.solde < self.frais_carte:
            raise ValueError("Solde insuffisant pour le renouvellement.")

        self.client.solde -= self.frais_carte
        self.client.save()

        self.numero_carte = generate_numero_carte()
        self.date_ouverture = timezone.now().date()
        self.date_expiration = self.date_ouverture + timedelta(days=2*365)
        self.cvc = str(random.randint(100, 999))
        self.is_active = True
        self.statut_carte = "active"
        self.frais_payes = True  

        self.save()

    

    def save(self, *args, **kwargs):
        plafonds = PLAFONDS_CARTES.get(self.type_carte, {"paiement": Decimal("5000.00"), "retrait": Decimal("2000.00")})
        self.plafond_paiement = plafonds["paiement"]
        self.plafond_retrait = plafonds["retrait"]
        if self.est_expiree():
            self.is_active = False
            self.statut_carte = "expirée"
        elif not self.is_active:
            self.statut_carte = "bloquée"
        super().save(*args, **kwargs)


    class Meta:
        constraints = [
            UniqueConstraint(fields=["client_id", "type_carte"], name="unique_carte_par_type_par_client")
        ]

    def __str__(self):
        return f"{self.get_type_carte_display()} - {self.numero_carte} (Expire le {self.date_expiration})- Frais payés: {'Oui' if self.frais_payes else 'Non'}"







class TypeCompte(models.Model):
    type_compte_id = models.AutoField(primary_key=True)  # Identifiant unique du type de compte
    nom_type = models.CharField(max_length=50)  # Nom du type de compte

    def __str__(self):
        return self.nom_type 


class Compte(models.Model): 
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence correcte
    type_compte = models.ForeignKey('TypeCompte', on_delete=models.CASCADE)  
    solde = models.DecimalField(max_digits=10, decimal_places=2)  
    date_ouverture = models.DateField()  
    statut = models.CharField(max_length=20)  
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
        self.soft_delete()

    def __str__(self):
        return f"Compte {self.compte_id} - Type: {self.type_compte.nom_type} - Client: {self.client.nom} {self.client.prenom}"

class TypeDocument(models.Model):
    type_document_id = models.AutoField(primary_key=True)  # Identifiant unique du type de document
    nom_type = models.CharField(max_length=50)  # Nom du type de document
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

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
    statut_verif = models.CharField(
        max_length=15, 
        choices=[('not verified', 'non vérifié'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], 
        default='not verified'
    )  # Statut de vérification
    demande = models.ForeignKey(DemandeCompteBancaire, on_delete=models.CASCADE, blank=True, null=True) #hna bash ndiro relation demandecreation ou document
    deleted_at=models.DateTimeField(null=True,blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    def delete(self, *args, **kwargs):
        request = kwargs.get("request")
        if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
        self.soft_delete()


    def __str__(self):
        return f"Document {self.document_id} - Type: {self.type_document.nom_type} - "



class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_token")
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.created_at < now() - timedelta(hours=24) 

    def __str__(self):
        return f"Token de vérification pour {self.user.email}"






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
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE,null=True)  # Référence au compte
    type_transaction = models.ForeignKey(TypeTransaction, on_delete=models.CASCADE)  # Référence au type de transaction
    montant = models.IntegerField()  # Montant de la transaction (minimum 500 DA)
    date_transaction = models.DateTimeField(auto_now_add=True)  # Date et heure de la transaction
    statut_transaction = models.CharField(max_length=50)  # Statut de la transaction (réussie, échouée)

    def clean(self):
        if self.montant < 500:
            raise ValidationError('Le montant doit être d\'au moins 500 DA.')

    def __str__(self):
        return f"Transaction {self.transaction_id} - Compte ID: {self.compte.compte_id} - Montant: {self.montant} - Statut: {self.statut_transaction}"
        



class ResultatIA(models.Model):
    resultat_id = models.AutoField(primary_key=True)  # Identifiant unique du résultat
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Référence au client concerné
    type_analyse = models.CharField(max_length=50)  # Type d'analyse
    resultat = models.CharField(max_length=50)  # Résultat de l'analyse
    date_analyse = models.DateField()  # Date de l'analyse

    def __str__(self):
        return f"Analyse {self.resultat_id} - {self.type_analyse} - {self.resultat} - {self.client.nom} {self.client.prenom}"




print("Mise à jour terminée !")

class Employe(models.Model):
    ROLE_CHOICES = [
        ('agent', 'Agent Bancaire'),
        ('admin', 'Administrateur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employe_profile", null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')
    deleted_at = models.DateTimeField(null=True, blank=True)
    emp_id = models.CharField(max_length=10, unique=True, primary_key=True, editable=False)
    def generate_unique_emp_id(self):
        """ Génère un emp_id unique sous la forme EMP123456 """
        while True:
            new_id = f"EMP{str(uuid.uuid4().int)[:6]}"
            if not Employe.objects.filter(emp_id=new_id).exists():
                return new_id

    def save(self, *args, **kwargs):
        # Générer un `emp_id` unique si inexistant
        if not self.emp_id:
            self.emp_id = self.generate_unique_emp_id()

        # Vérifier si un utilisateur existe avec cet email
        if self.user and User.objects.filter(email=self.user.email).exclude(id=self.user.id).exists():
            raise ValidationError(f"Un utilisateur avec l'email {self.user.email} existe déjà.")

        # Si aucun utilisateur n'est associé, en créer un
        if not self.user:
            try:
                user = User.objects.create(
                    username=f"emp_{int(now().timestamp())}",
                    email="",  # Pas d'email par défaut
                    is_staff=True
                )
                self.user = user
            except IntegrityError:
                raise ValidationError(f"L'utilisateur avec cet email existe déjà.")

        # Assurer que l'utilisateur est bien un staff (employé)
        if self.user and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username if self.user else 'Sans utilisateur'} - {self.get_role_display()}"

    def soft_delete(self):
        """Soft delete de l'employé et de son User"""
        self.deleted_at = now()
        self.save()
        
        

    def delete(self, *args, **kwargs):
     """Empêcher les agents de supprimer"""
     request = kwargs.get("request")
    
     if request and hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
        raise PermissionDenied("Les agents bancaires ne peuvent pas supprimer des documents.")
    
     # Vérification si self.user existe avant de tenter de l'utiliser
    
    
     self.soft_delete() 
     if hasattr(self, "user") and self.user:
        self.user.deleted_at = now()  # Marquer l'utilisateur comme supprimé
        self.user.save(update_fields=["deleted_at"])  # Sauvegarder uniquement ce champ
     if hasattr(self, "conferences_employe"):
        for conference in self.conferences_employe.all():
            conference.soft_delete()

     # Supprimer l'instance pour éviter qu'elle continue d'exister en mémoire
  
    # Utilisation de la méthode soft_delete() de l'employé
    def restore(self):
     """Restaure un employé et ses vidéoconférences"""
     self.deleted_at = None
     self.save()

    # ✅ Restaurer les vidéoconférences associées
     if hasattr(self, "conferences_employe"):
        for conference in self.conferences_employe.all():
            conference.deleted_at = None
            conference.save()

    # ✅ Restaurer l'utilisateur associé
     if hasattr(self, "user") and self.user:
        self.user.deleted_at = None
        self.user.save(update_fields=["deleted_at"])






from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db import models

class VideoConference(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("done", "Terminée"),
        ("canceled", "Annulée"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="conferences_client")
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="conferences_employe", to_field="emp_id")
    meeting_url = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    
    

    def clean(self):
     """Validation pour empêcher une date passée sauf si on ne modifie que le statut."""

    # ✅ Ignorer la validation si la vidéoconférence est supprimée (soft delete)
     if self.deleted_at:
       return

     if self.scheduled_at is None:
        raise ValidationError("La date de la vidéoconférence doit être spécifiée.")

    # ✅ Vérifier si la modification concerne uniquement le statut
     if self.pk:  # Vérifie si l'objet existe déjà
        existing_instance = VideoConference.objects.get(pk=self.pk)
        if existing_instance.scheduled_at != self.scheduled_at:  # La date a changé ?
            if self.scheduled_at < now():
                raise ValidationError("La date de la vidéoconférence ne peut pas être dans le passé.")

    # ✅ Vérification de l'unicité uniquement pour les vidéoconférences actives et futures
     if VideoConference.objects.filter(
        client=self.client,
        employe=self.employe,
        status="pending",
        deleted_at__isnull=True,  # Ne prendre que les vidéoconférences non supprimées
        scheduled_at__gte=now()   # ✅ Ignorer les vidéoconférences expirées !
    ).exclude(pk=self.pk).exists():
        raise ValidationError("Il existe déjà une vidéoconférence en attente pour ce client et cet employé.")

     super().clean()



    def save(self, *args, **kwargs):
        """Vérifie les contraintes avant la sauvegarde"""
        self.clean()  # Appelle la validation

        if not self.client or not self.employe:
            raise ValueError("Le client et l'employé doivent être définis avant d'enregistrer.")

        # Vérifie que le client et l'employé existent bien en base de données
        if not Client.objects.filter(client_id=self.client.client_id).exists():
            raise ValueError(f"Le client avec l'ID {self.client.client_id} n'existe pas.")

        if not Employe.objects.filter(emp_id=self.employe.emp_id).exists():
            raise ValueError(f"L'employé avec l'ID {self.employe.emp_id} n'existe pas.")

        if not self.meeting_url:
            self.meeting_url = f"https://meet.jit.si/{self.client.client_id}{self.employe.emp_id}"
        
        

        super().save(*args, **kwargs)
    def soft_delete(self):
        """Marque la vidéoconférence comme supprimée au lieu de la supprimer réellement."""
        self.deleted_at = timezone.now()
        self.status="canceled"
        self.save()



    def delete(self, *args, **kwargs):
        """Applique le soft delete au lieu d’une suppression définitive."""
        self.soft_delete()
    













