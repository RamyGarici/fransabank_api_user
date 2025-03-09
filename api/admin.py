from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AlreadyRegistered
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from api.models import User, Profile, TypeDocument, DemandeCompteBancaire, Document, Client, Employe

class BaseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(deleted_at__isnull=True)
        return qs

    def has_delete_permission(self, request, obj=None):
        if request.user.is_staff:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.is_staff:
            return False
        return super().has_change_permission(request, obj)

class UserAdmin(BaseAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser']
    list_filter = ['is_staff']

    @admin.action(description="Promouvoir en Agent Bancaire")
    def promouvoir_agent(self, request, queryset):
        agent_group, created = Group.objects.get_or_create(name="Agent Bancaire")
        for user in queryset:
            user.groups.add(agent_group)
        self.message_user(request, "Les utilisateurs sélectionnés sont maintenant des Agents Bancaires.")

    @admin.action(description="Rétrograder en Utilisateur Classique")
    def retrograder_agent(self, request, queryset):
        agent_group = Group.objects.filter(name="Agent Bancaire").first()
        if agent_group:
            for user in queryset:
                user.groups.remove(agent_group)
            self.message_user(request, "Les utilisateurs sélectionnés sont redevenus des utilisateurs normaux.")

    actions = [promouvoir_agent, retrograder_agent]

class EmployeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

class DocumentInline(admin.TabularInline):  
    model = Document
    extra = 1  
    fields = ('type_document', 'fichier_link', 'statut_verif')  
    readonly_fields = ('fichier_link',)  

    def fichier_link(self, obj):
        if obj.fichier:
            return format_html('<a href="{}" target="_blank">Voir le document</a>', obj.fichier.url)
        return "Aucun fichier"

    fichier_link.short_description = "Document"

class ProfileAdmin(BaseAdmin):
    list_display = ['user', 'get_date_of_birth', 'get_phone_number']
    search_fields = ('user__username', 'user__date_of_birth', 'user__phone_number')

    def get_date_of_birth(self, obj):
        return obj.date_of_birth if hasattr(obj, 'date_of_birth') else None
    get_date_of_birth.short_description = "Date de naissance"

    def get_phone_number(self, obj):
        return obj.phone_number if hasattr(obj, 'phone_number') else None
    get_phone_number.short_description = "Numéro de téléphone"

class DemandeCompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [DocumentInline]

    def get_clients(self, obj):
        return ", ".join([client.user.username for client in obj.client.all()]) if obj.client.exists() else "Aucun client"
    get_clients.short_description = "Clients"


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_id', 'get_balance')

    def get_account_number(self, obj):
        return obj.account_number if hasattr(obj, 'account_number') else None
    get_account_number.short_description = "Numéro de compte"

    def get_balance(self, obj):
        return obj.balance if hasattr(obj, 'balance') else None
    get_balance.short_description = "Solde"

# Enregistrement des modèles avec gestion d'erreur AlreadyRegistered
models = [
    (Employe, EmployeAdmin),
    (User, UserAdmin),
    (Profile, ProfileAdmin),
    (TypeDocument, None),
    (DemandeCompteBancaire, DemandeCompteBancaireAdmin),
    (Client, ClientAdmin),
]

for model, admin_class in models:
    try:
        admin.site.register(model, admin_class)
    except AlreadyRegistered:
        pass  # Ignore l'erreur si le modèle est déjà enregistré

