from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Client

User = get_user_model()  # Utilise le bon User

class ClientBackend(BaseBackend):
    def authenticate(self, request, client_id=None, password=None):
        try:
            client = Client.objects.get(client_id=client_id)
            user = client.user  # Associer le Client à son User
            if user and user.check_password(password):  # Vérifie bien avec Django
                return user
        except Client.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)  # Vérifie avec get_user_model()
        except User.DoesNotExist:
            return None
