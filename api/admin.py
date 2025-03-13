from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django import forms
from django.contrib import messages
from api.models import User, Employe, Profile, TypeDocument, DemandeCompteBancaire, Document, Client, cartebancaire,VideoConference

import logging

logger = logging.getLogger(__name__)

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
    list_display = ['deleted_at' ]

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
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'deleted_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']


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
    list_display = ['emp_id','username', 'email', 'first_name', 'last_name', 'role', 'deleted_at', ]
    form = EmployeAdminForm  # Utilisation du formulaire personnalisé
    search_fields = ('emp_id', 'user__email','user__username','user__first_name','user__last_name')
    


    fieldsets = (
        ("Informations de l'employé", {
            "fields": ("role",),
        }),
        ("Informations utilisateur", {
            "fields": ("username", "email", "first_name", "last_name", "password"),
        }),
    )
    readonly_fields=('emp_id',)

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
            user.set_password(form.cleaned_data.get("password"))  # Hache le mot de passe
            user.save()
            obj.user = user  # Associe le nouvel utilisateur à l'Employé
        else:
        # Si l'utilisateur existe déjà et qu'un mot de passe a été modifié
          if "password" in form.changed_data:
            obj.user.password = make_password(form.cleaned_data["password"])
            obj.user.save()
 

        obj.save()  # Sauvegarde l'Employé


### 📌 Admin Carte Bancaire ###
class CarteBancaireInline(admin.TabularInline):
    model = cartebancaire
    extra = 0
    fields = ("numero_carte", "type_carte", "date_expiration", "statut_carte", "is_active")
    readonly_fields = ("numero_carte", "type_carte", "date_expiration", "statut_carte")


### 📌 Admin Profil ###
class ProfileAdmin(BaseAdmin):
    list_display = ['user', 'first_name','last_name','first_name', 'deleted_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False)
    def email(self, obj):
        return obj.user.email if obj.user else "-"


### 📌 Admin Type Document ###
class TypeDocumentAdmin(BaseAdmin):
    list_display = ['nom_type', 'deleted_at']





### 📌 Admin Demande de compte ###
class DemandeCompteBancaireAdmin(BaseAdmin):
    list_display = ['user', 'status', 'created_at', 'deleted_at']
    list_filter = ['status', SoftDeleteFilter]
    def get_readonly_fields(self, request, obj=None):
        """Permet uniquement la modification du statut pour les agents bancaires"""
        if hasattr(request.user, "employe_profile") and request.user.employe_profile.role == "agent":
            return [field.name for field in self.model._meta.fields if field.name != "status"]
        return super().get_readonly_fields(request, obj)




### 📌 Admin Client ###
class ClientAdmin(BaseAdmin):
    list_display = ['user', 'client_id','user__email','nom','prenom', 'deleted_at']
    inlines = [CarteBancaireInline]
    search_fields = (
        "user__email", 
        "client_id", 
        "prenom",  # Prénom de l'utilisateur
        "nom",   # Nom de l'utilisateur
        "user__username",    # Nom d'utilisateur
        "client_id",          # ID de l'utilisateur
    )

    





class VideoConferenceAdminForm(forms.ModelForm):
    meeting_url_preview = forms.CharField(
        label="URL de la réunion",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly", "style": "width: 100%; font-weight: bold; color: blue;"}),
    )

    class Meta:
        model = VideoConference
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["meeting_url_preview"].initial = self.instance.meeting_url

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        employe = cleaned_data.get("employe")
        if client and employe:
            generated_url = f"https://meet.jit.si/{client.client_id}{employe.emp_id}"
            cleaned_data["meeting_url"] = generated_url
            self.cleaned_data["meeting_url_preview"] = generated_url  # Met à jour le champ affiché
        return cleaned_data

class VideoConferenceAdmin(admin.ModelAdmin):
    form = VideoConferenceAdminForm  
    list_display = ("client", "employe", "scheduled_at", "status", "meeting_url", "plannifier_visio")
    list_filter = ("status", "scheduled_at")
    search_fields = ("client__client_id", "client__user__email", "employe__user__email")
    ordering = ("scheduled_at",)
    raw_id_fields = ("employe","client")
  
    readonly_fields = ("meeting_url",)

    fieldsets = (
        (None, {
            "fields": ("client", "employe", "scheduled_at", "status", "meeting_url_preview"),
        }),
    )
    class Media:
        js = ("admin/js/video_conference.js",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(client__isnull=False)

    @admin.display(description="Planification")
    def plannifier_visio(self, obj):
        if obj.scheduled_at:
            return format_html(f"📅 <b>{obj.scheduled_at.strftime('%d/%m/%Y %H:%M')}</b>")
        return "Non planifiée"





   

### 📌 Enregistrement des modèles ###
admin.site.register(User, UserAdmin)
admin.site.register(Employe, EmployeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TypeDocument, TypeDocumentAdmin)
admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireAdmin)
admin.site.register(Client, ClientAdmin)
admin_site.register(VideoConference, VideoConferenceAdmin)
