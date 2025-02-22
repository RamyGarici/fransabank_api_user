from django.contrib import admin
from api.models import User, Profile
from .models import TypeDocument 
from .models import DemandeCompteBancaire ,Document

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
    extra = 1  # Nombre de champs vides à afficher pour ajouter de nouveaux documents
    fields = ('type_document', 'fichier', 'statut_verif',)
#reglage bash ndiro ghir les demandes li status mashi approuvé
@admin.register(DemandeCompteBancaire)
class DemandeCompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')  # Colonnes affichées
    search_fields = ('user__email', 'status')  # Barre de recherche
    list_filter = ('status',)
    inlines = [DocumentInline]
#hadi pour trier la liste des demandes ou ndiro ceux approuvées whdhom ou rejeté whdohom
#class DemandeCompteBancaireApprouveeAdmin(DemandeCompteBancaireAdmin):
    #def get_queryset(self, request):
        #return super().get_queryset(request).filter(status='approved')

#admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireAdmin) 
#admin.site.register(DemandeCompteBancaire, DemandeCompteBancaireApprouveeAdmin)