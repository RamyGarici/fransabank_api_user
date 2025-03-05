from django.contrib import admin
from django.contrib.admin import actions
from api.models import User, Profile, Employe
from .models import TypeDocument, DemandeCompteBancaire, Document, Client
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.auth.models import Group

class BaseAdmin(admin.ModelAdmin):
   
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="Agent Bancaire").exists():
            return qs.filter(deleted_at__isnull=True)
        return qs

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name="Agent Bancaire").exists():
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return not request.user.groups.filter(name="Agent Bancaire").exists()

class DeletedAtFilter(admin.SimpleListFilter):
    title = _("Statut de suppression")  
    parameter_name = "deleted_at"

    def lookups(self, request, model_admin):
        return [
            ("active", _("Actifs (non supprimés)")),
            ("deleted", _("Supprimés")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(deleted_at__isnull=True)
        if self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        return queryset

class AgentBancaireFilter(admin.SimpleListFilter):
    title = "Types d'utilisateur"
    parameter_name = "agent_bancaire"

    def lookups(self, request, model_admin):
        return [("yes", "Agents Bancaires"), ("no", "Utilisateurs Classiques")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(groups__name="Agent Bancaire")
        return queryset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'is_mobile_user']
    list_filter = ('is_employe',)  # Filtrer par le champ is_employe

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Exclure les employés de la liste des utilisateurs
        return qs.filter(is_employe=False)

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

class ProfileAdmin(BaseAdmin):
    list_editable = ['verified']
    list_display = ['user', 'first_name', 'last_name', 'verified']
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = (DeletedAtFilter,)

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

@admin.register(DemandeCompteBancaire)
class DemandeCompteBancaireAdmin(BaseAdmin):
    list_display = ('user', 'last_name', 'first_name', 'status', 'created_at')
    search_fields = ('user__email', 'user__username', 'status', 'first_name', 'last_name')
    list_filter = ('status', DeletedAtFilter)
    inlines = [DocumentInline]

@admin.register(Client)
class ClientAdmin(BaseAdmin):
    list_display = ("id", "nom", "email", "created_at")
    search_fields = ("nom", "email")
    list_filter = (DeletedAtFilter,)

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role']
    list_filter = ('role',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtrer uniquement les employés
        return qs.filter(is_employe=True)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name="Agent Bancaire").exists():
            return obj and obj.role == 'agent'
        return super().has_change_permission(request, obj)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(TypeDocument)