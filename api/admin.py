from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django import forms
from django.contrib import messages
from api.models import User, Employe, Profile, TypeDocument, DemandeCompteBancaire, Document, Client

import logging

logger = logging.getLogger(__name__)

from api.models import User, Employe, Profile, TypeDocument, DemandeCompteBancaire, cartebancaire, Client



### 📌 Filtre Soft Delete ###
class SoftDeleteFilter(admin.SimpleListFilter):
    title = "État de suppression"
    parameter_name = "deleted_at"

    def lookups(self, request, model_admin):
        return [('active', "Non supprimés"), ('deleted', "Supprimés")]

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(deleted_at__isnull=True)
        if self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        return queryset


### 📌 Base Admin avec Soft Delete ###
class BaseAdmin(admin.ModelAdmin):
    list_filter = (SoftDeleteFilter,)
    list_display = ['deleted_at', 'soft_delete_button']

    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for obj in qs:
            obj._request = request  # Injecte request dans chaque objet pour l'utiliser dans soft_delete_button
        return qs if request.user.is_superuser else qs.filter(deleted_at__isnull=True)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return (SoftDeleteFilter,)
        return ()

    def has_delete_permission(self, request, obj=None):
       
        
        if hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
           
            return False  # Bloquer la suppression

        print("✅ Suppression autorisée")
        return True

    def get_actions(self, request):
        """Désactive complètement la suppression pour les agents"""
        actions = super().get_actions(request)
        if hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            if "delete_selected" in actions:
                del actions["delete_selected"]  # Supprime l'action de suppression en masse
        return actions

    def delete_model(self, request, obj):
        """Empêche les agents bancaires de supprimer tout objet."""
        if hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            messages.error(request, "Vous n'avez pas l'autorisation de supprimer cet objet.")
            return  # Bloque la suppression

        # Appliquer le soft delete pour les autres utilisateurs
        obj.deleted_at = now()
        obj.save()
        messages.success(request, "L'élément a été soft supprimé.")

    def soft_delete_button(self, obj):
        """Affiche 🗑️ pour soft delete et ✅ pour restaurer, sauf pour les agents"""
        if not obj.pk:
           return "-"

        request = getattr(obj, "_request", None)
        is_agent = False

        if request:
          is_agent = getattr(request.user, "employe_profile", None) and getattr(request.user.employe_profile, "role", None) == "agent"
          if is_agent:
            return "-"  # Cacher complètement le bouton pour les agents

        url_name = "restore" if obj.deleted_at else "soft_delete"
        url = reverse(f'admin:{url_name}', args=[obj._meta.model_name, obj.pk])
        emoji = "✅" if obj.deleted_at else "🗑️"
        color = "green" if obj.deleted_at else "red"

        return format_html('<a href="{}" style="color: {}; font-size: 18px;">{}</a>', url, color, emoji)

    soft_delete_button.short_description = "Action"





### 📌 Vue pour gérer le Soft Delete et la restauration ###
class MyAdminSite(admin.AdminSite):
    site_header = "Administration bancaire"
    site_title = "Admin Banque"
    index_title = "Bienvenue dans l'admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('soft_delete/<str:model>/<int:object_id>/', self.soft_delete_view, name='soft_delete'),
            path('restore/<str:model>/<int:object_id>/', self.restore_view, name='restore'),
        ]
        return custom_urls + urls

    def get_model_class(self, model_name):
        """Retourne la classe du modèle en fonction de son nom."""
        for model in admin.site._registry:
            if model._meta.model_name == model_name:
                return model
        return None

    def soft_delete_view(self, request, model, object_id):
        """Soft delete un objet dynamiquement"""
        model_class = self.get_model_class(model)
        if not model_class:
            messages.error(request, "Modèle introuvable.")
            return HttpResponseRedirect('/admin/')

        obj = model_class.objects.filter(pk=object_id).first()
        if obj:
            obj.deleted_at = now()
            obj.save()
            messages.success(request, "L'élément a été soft supprimé.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def restore_view(self, request, model, object_id):
        """Restaure un objet soft deleted dynamiquement"""
        model_class = self.get_model_class(model)
        if not model_class:
            messages.error(request, "Modèle introuvable.")
            return HttpResponseRedirect('/admin/')

        obj = model_class.objects.filter(pk=object_id).first()
        if obj:
            obj.deleted_at = None
            obj.save()
            messages.success(request, "L'élément a été restauré.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    


admin_site = MyAdminSite()
admin.site = admin_site


### 📌 Admin Utilisateur ###
class UserAdmin(BaseAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'deleted_at', 'soft_delete_button']


### 📌 Formulaire Employé ###
class EmployeAdminForm(forms.ModelForm):
    """Formulaire permettant d'éditer les informations d'un employé et de son utilisateur."""
    
    email = forms.EmailField(label="Email", required=True)
    username = forms.CharField(label="Nom d'utilisateur", required=True)
    first_name = forms.CharField(label="Prénom", required=True)
    last_name = forms.CharField(label="Nom", required=True)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Employe
        fields = ['role']  # On gère seulement "role", le reste vient du modèle User

    def __init__(self, *args, **kwargs):
        """Pré-remplit les champs avec les valeurs de l'utilisateur associé."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        """Sauvegarde l'utilisateur et l'employé ensemble."""
        employe = super().save(commit=False)
        user = employe.user if employe.user_id else User()

        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])  # Met à jour le mot de passe

        user.is_staff = True  # S'assure que l'utilisateur est bien un employé
        user.save()

        employe.user = user
        if commit:
            employe.save()
        return employe





class EmployeAdmin(BaseAdmin):
    """Admin Django pour les employés."""
    
    list_filter = ['role', SoftDeleteFilter]
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'deleted_at', 'soft_delete_button']
    form = EmployeAdminForm  # Utilisation du formulaire personnalisé

    fieldsets = (
        ("Informations de l'employé", {
            "fields": ("role",),
        }),
        ("Informations utilisateur", {
            "fields": ("username", "email", "first_name", "last_name", "password"),
        }),
    )

    def username(self, obj):
        return obj.user.username if obj.user else "-"

    def email(self, obj):
        return obj.user.email if obj.user else "-"

    def first_name(self, obj):
        return obj.user.first_name if obj.user else "-"

    def last_name(self, obj):
        return obj.user.last_name if obj.user else "-"

    username.short_description = "Nom d'utilisateur"
    email.short_description = "Email"
    first_name.short_description = "Prénom"
    last_name.short_description = "Nom"

    def get_readonly_fields(self, request, obj=None):
        """Empêche les agents bancaires de modifier leur rôle et leurs identifiants."""
        if hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            return ("role", "username", "email", "first_name", "last_name")  # L'agent bancaire ne peut rien modifier
        return ()  # Permet la modification pour les autres utilisateurs

    def save_model(self, request, obj, form, change):
        """Créer automatiquement un User si l'Employé n'en a pas"""
        if not obj.user_id:  # Si aucun User n'est associé
            user = User.objects.create(
                username=f"emp_{int(now().timestamp())}",
                email=form.cleaned_data.get("email", ""),
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                is_staff=True
            )
            obj.user = user  # Associe le nouvel utilisateur à l'Employé

        obj.save()  # Sauvegarde l'Employé





class CarteBancaireInline(admin.TabularInline):  
    model = cartebancaire
    extra = 0  
    fields = ("numero_carte", "type_carte", "date_expiration", "statut_carte","is_active")  
    readonly_fields = ("numero_carte", "type_carte", "date_expiration", "statut_carte")  












    



### 📌 Admin Profil ###
class ProfileAdmin(BaseAdmin):
    list_display = ['user', 'first_name', 'last_name', 'deleted_at', 'soft_delete_button']
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False)


### 📌 Admin Type Document ###
class TypeDocumentAdmin(BaseAdmin):
    list_display = ['nom_type', 'deleted_at', 'soft_delete_button']


### 📌 Admin Demande de compte ###
class DemandeCompteBancaireAdmin(BaseAdmin):
    list_display = ['user', 'status', 'created_at', 'deleted_at', 'soft_delete_button']
    list_filter = ['status', SoftDeleteFilter]




### 📌 Admin Client ###
class ClientAdmin(BaseAdmin):
    list_display = ['user', 'client_id', 'deleted_at', 'soft_delete_button']
    inlines = [CarteBancaireInline]


### 📌 Enregistrement des modèles ###
admin.site.register(User, UserAdmin)
admin.site.register(Employe, EmployeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TypeDocument, TypeDocumentAdmin)
admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireAdmin)
admin.site.register(Client, ClientAdmin)