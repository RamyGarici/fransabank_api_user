from django.contrib import admin
from api.models import User, Profile
from .models import TypeDocument 
from .models import Document

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

class ProfileAdmin(admin.ModelAdmin):
    list_editable=['verified']
    list_display = ['user','first_name','last_name',  'verified']

admin.site.register(User, UserAdmin) 
admin.site.register(Profile, ProfileAdmin)  
admin.site.register(TypeDocument)
admin.site.register(Document)