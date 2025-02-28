from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from api.models import Client, Profile, DemandeCompteBancaire

@receiver(post_migrate)
def create_agent_bancaire_group(sender, **kwargs):
    group, created = Group.objects.get_or_create(name="Agent Bancaire")

    content_types = [
        ContentType.objects.get_for_model(Client),
        ContentType.objects.get_for_model(Profile),
        ContentType.objects.get_for_model(DemandeCompteBancaire),
    ]

    permissions = Permission.objects.filter(content_type__in=content_types, codename__in=[
        "view_client", "view_profile", "view_demande", "change_demande"
    ])

    group.permissions.set(permissions)
    print(" Groupe 'Agent Bancaire' et permissions configurés.")
