from django.contrib import admin
from api.models import User, Profile
from .models import TypeDocument 
from .models import DemandeCompteBancaire ,Document
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

class ProfileAdmin(admin.ModelAdmin):
    list_editable=['verified']
    list_display = ['user','first_name','last_name',  'verified']

admin.site.register(User, UserAdmin) 
admin.site.register(Profile, ProfileAdmin)  
admin.site.register(TypeDocument)

class DocumentInline(admin.TabularInline):  
    model = Document
    extra = 1  # Nombre de champs vides pour ajouter de nouveaux documents
    fields = ('type_document', 'fichier_link', 'statut_verif')  # Utiliser fichier_link au lieu de fichier
    readonly_fields = ('fichier_link',)  # Rendre le lien non modifiable

    def fichier_link(self, obj):
        if obj.fichier:
            return format_html('<a href="{}" target="_blank">Voir le document</a>', obj.fichier.url)
        return "Aucun fichier"

    fichier_link.short_description = "Document"  # Correction de l'indentation
#reglage bash ndiro ghir les demandes li status mashi approuvé
#@admin.register(DemandeCompteBancaire)
#class DemandeCompteBancaireAdmin(admin.ModelAdmin):
 #   list_display = ('user', 'status', 'created_at')  # Colonnes affichées
 #   search_fields = ('user__email', 'status')  # Barre de recherche
  #  list_filter = ('status',)
   # inlines = [DocumentInline]
#hadi pour trier la liste des demandes ou ndiro ceux approuvées whdhom ou rejeté whdohom
#class DemandeCompteBancaireApprouveeAdmin(DemandeCompteBancaireAdmin):
    #def get_queryset(self, request):
        #return super().get_queryset(request).filter(status='approved')

#admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireAdmin) 
#admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireApprouveeAdmin)
@admin.register(DemandeCompteBancaire)
class DemandeCompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')  
    search_fields = ('user__email','user__username', 'status')  
    list_filter = ('status',)  # Permet de filtrer par statut
    inlines = [DocumentInline]

    # Actions personnalisées pour modifier le statut
    @admin.action(description="Marquer comme approuvé")
    def approuver_demandes(self, request, queryset):
        queryset.update(status="Approuvée")

    @admin.action(description="Marquer comme rejeté")
    def rejeter_demandes(self, request, queryset):
        queryset.update(status="Rejetée")

    actions = [approuver_demandes, rejeter_demandes]