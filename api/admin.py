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

from api.models import User, Employe, Profile, TypeDocument, DemandeCompteBancaire, Document, Client



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
        return qs if request.user.is_superuser else qs.filter(deleted_at__isnull=True)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return (SoftDeleteFilter,)
        return ()

    def has_add_permission(self, request):
        return request.user.is_superuser  # Seul l'admin peut ajouter

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser  # Seul l'admin peut modifier

    def delete_model(self, request, obj):
        obj.deleted_at = now()
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Seuls les super admins peuvent supprimer

    def soft_delete_button(self, obj):
        """Affiche 🗑️ pour soft delete et ✅ pour restaurer"""
        if not obj.pk:
            return "-"

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

    def get_app_list(self, request):
        """Personnalise la liste des modèles visibles en fonction de l'utilisateur."""
        logger.debug(f"🔎 Utilisateur connecté: {request.user.username}, is_superuser={request.user.is_superuser}, is_staff={request.user.is_staff}")

        app_list = super().get_app_list(request)

        if request.user.is_superuser:
            return app_list  # Le superadmin voit tout

        new_app_list = []
        for app in app_list:
            new_models = []
            for model in app["models"]:
                model_name = model["object_name"].lower()
                logger.debug(f"📌 Vérification du modèle: {model_name}")

                # 🔴 Agent bancaire : ne voit que les demandes, documents, clients et profils
                if request.user.is_staff and not request.user.is_superuser:
                    if model_name in ["demandecomptebancaire", "typedocument", "client", "profile"]:
                        logger.debug(f"✅ Ajouté pour agent bancaire: {model_name}")
                        new_models.append(model)

                # 🟢 Admin normal : ne voit pas "User"
                elif request.user.is_staff:
                    if model_name not in ["user"]:
                        logger.debug(f"✅ Ajouté pour admin: {model_name}")
                        new_models.append(model)

            if new_models:
                app["models"] = new_models
                new_app_list.append(app)

        logger.debug(f"📢 Modèles finaux affichés: {[model['object_name'] for app in new_app_list for model in app['models']]}")
        return new_app_list


admin_site = MyAdminSite()
admin.site = admin_site


### 📌 Admin Utilisateur ###
class UserAdmin(BaseAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'deleted_at', 'soft_delete_button']


### 📌 Formulaire Employé ###
class EmployeAdminForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Nom d'utilisateur")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Employe
        fields = ['role']

    def save(self, commit=True):
        employe = super().save(commit=False)
        user = employe.user if employe.user_id else User()

        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if self.cleaned_data['password']:
            user.password = make_password(self.cleaned_data['password'])

        user.is_staff = True
        user.save()

        employe.user = user
        if commit:
            employe.save()
        return employe


### 📌 Admin Employé ###
class EmployeAdmin(BaseAdmin):
    list_filter = ['role', SoftDeleteFilter]
    list_display = ['user', 'role', 'deleted_at', 'soft_delete_button']
    form = EmployeAdminForm


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

    def has_add_permission(self, request):
        return False  # Personne ne peut ajouter

    def has_delete_permission(self, request, obj=None):
        return False  # Personne ne peut supprimer


### 📌 Admin Client ###
class ClientAdmin(BaseAdmin):
    list_display = ['user', 'client_id', 'deleted_at', 'soft_delete_button']


### 📌 Enregistrement des modèles ###
admin.site.register(User, UserAdmin)
admin.site.register(Employe, EmployeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TypeDocument, TypeDocumentAdmin)
admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireAdmin)
admin.site.register(Client, ClientAdmin)