from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from api.models import Employe,Profile,VideoConference,Client
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import DemandeCompteBancaire
from django.db.models.signals import pre_delete

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
        content_type__model__in=["profile", "demandecomptebancaire", "client", "typedocument","videoconference"],
        codename__startswith="view_"  # Seulement lecture
    )
    agent_group.permissions.set(agent_permissions)

    # Ajouter la permission spécifique de modification uniquement pour les demandes de compte
    demande_ct = ContentType.objects.get_for_model(DemandeCompteBancaire)
    change_permission, _ = Permission.objects.get_or_create(
        codename="change_demandecomptebancaire",
        content_type=demande_ct
    )
    video_conf_ct = ContentType.objects.get_for_model(VideoConference)  # Assure-toi que c'est bien le bon modèle
    add_permission, _ = Permission.objects.get_or_create(
        codename="add_videoconference",
         content_type=video_conf_ct
)
    change_video_permission, _ = Permission.objects.get_or_create(
     codename="change_videoconference",
     content_type=video_conf_ct
)
    agent_group.permissions.add(change_video_permission)
    agent_group.permissions.add(add_permission)
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
@receiver(pre_delete, sender=Profile)
def delete_user_when_profile_deleted(sender, instance, **kwargs):
    print("Signal pre_delete déclenché pour le profil:", instance)
    if instance.user:
        print("Suppression de l'utilisateur associé:", instance.user)
        instance.user.delete()
    else:
        print("Aucun utilisateur associé à ce profil.")


@receiver(pre_delete, sender=Client)
def soft_delete_client_conferences(sender, instance, **kwargs):
    """Soft delete toutes les vidéoconférences associées à un client supprimé."""
    for conference in instance.conferences_client.all():
        conference.soft_delete()

@receiver(pre_delete, sender=Employe)
def soft_delete_employe_conferences(sender, instance, **kwargs):
    """Soft delete toutes les vidéoconférences associées à un employé supprimé."""
    for conference in instance.conferences_employe.all():
        conference.soft_delete()