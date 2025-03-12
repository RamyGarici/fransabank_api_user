from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse

class PreventSoftDeletedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié
        if request.user.is_authenticated:
            # Vérifier si l'utilisateur est soft deleted
            if request.user.is_deleted():
                # Déconnecter l'utilisateur
                logout(request)
                # Ajouter un message d'erreur (optionnel)
                messages.error(request, "Votre compte a été désactivé.")
                # Rediriger vers la page de connexion
                return redirect(reverse('login'))  # Remplacez 'login' par le nom de votre vue de connexion

        # Si tout va bien, continuer la requête
        response = self.get_response(request)
        return response
