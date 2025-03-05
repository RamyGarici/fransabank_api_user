from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from api.models import Client, Profile, DemandeCompteBancaire, Employe

@receiver(post_migrate)
def create_agent_bancaire_group(sender, **kwargs):
    """
    Signal pour créer le groupe "Agent Bancaire" et lui attribuer les permissions nécessaires
    après chaque migration.
    """
    # Créer ou récupérer le groupe "Agent Bancaire"
    group, created = Group.objects.get_or_create(name="Agent Bancaire")

    # Définir les modèles pour lesquels les permissions doivent être attribuées
    content_types = [
        ContentType.objects.get_for_model(Client),  # Modèle Client
        ContentType.objects.get_for_model(Profile),  # Modèle Profile
        ContentType.objects.get_for_model(DemandeCompteBancaire),  # Modèle DemandeCompteBancaire
        ContentType.objects.get_for_model(Employe),  # Modèle Employe
    ]

    # Filtrer les permissions nécessaires pour ces modèles
    permissions = Permission.objects.filter(
        content_type__in=content_types,
        codename__in=[
            "view_client",  # Permission pour voir les clients
            "view_profile",  # Permission pour voir les profils
            "view_demande",  # Permission pour voir les demandes
            "change_demande",  # Permission pour modifier les demandes
            "view_employe",  # Permission pour voir les employés
        ]
    )

    # Attribuer les permissions au groupe "Agent Bancaire"
    group.permissions.set(permissions)

    # Afficher un message de confirmation dans la console
    print("Groupe 'Agent Bancaire' et permissions configurés.")