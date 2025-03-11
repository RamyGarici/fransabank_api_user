from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from api.models import Employe
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import DemandeCompteBancaire

def setup_roles():
    """Crée les groupes et assigne les permissions aux rôles."""
    

    # Créer ou récupérer les groupes
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    agent_group, _ = Group.objects.get_or_create(name="Agent")

    # Donner toutes les permissions à l'admin sauf sur le modèle User
    admin_permissions = Permission.objects.exclude(content_type__model="user")
    admin_group.permissions.set(admin_permissions)

    # Donner aux agents bancaires uniquement les permissions de lecture
    agent_permissions = Permission.objects.filter(
        content_type__model__in=["profile", "demandecomptebancaire", "client", "typedocument"],
        codename__startswith="view_"  # Seulement lecture
    )
    agent_group.permissions.set(agent_permissions)

    # Ajouter la permission spécifique de modification uniquement pour les demandes de compte
    demande_ct = ContentType.objects.get_for_model(DemandeCompteBancaire)
    change_permission, _ = Permission.objects.get_or_create(
        codename="change_demandecomptebancaire",
        content_type=demande_ct
    )
    agent_group.permissions.add(change_permission)
    agent_group.permissions.remove(*Permission.objects.filter(codename__startswith="delete_"))
    


@receiver(post_save, sender=Employe)
def assign_role(sender, instance, created, **kwargs):
    if created:
        setup_roles()

        # Assigner le groupe en fonction du rôle
        group_name = "Admin" if instance.role == "admin" else "Agent"
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.user.groups.set([group])

        # Supprimer les permissions de suppression individuelles
        if instance.role == "agent":
            instance.user.user_permissions.remove(*Permission.objects.filter(codename__startswith="delete_"))
            instance.user.is_staff = True  # Laisse l'accès à l'admin mais en lecture/modification limitée
        else:
            instance.user.is_staff = True  # L'admin a un accès complet

        instance.user.save()

