import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)
User = get_user_model()

class NoSoftDeletedAdminBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Django utilise `email` comme identifiant (USERNAME_FIELD = 'email')
            user = User.objects.get(email=username)
            
            logger.info(f"Tentative de connexion pour l'utilisateur : {username}")
            
            # Vérifier si l'utilisateur est soft deleted
            if user.deleted_at is not None:
                logger.warning(f"❌ Connexion refusée : utilisateur soft deleted - {username}")
                raise PermissionDenied("Ce compte a été désactivé.")
            
            # Vérifier le mot de passe
            if user.check_password(password):
                logger.info(f"✅ Connexion réussie pour l'utilisateur : {username}")
                return user
            else:
                logger.warning(f"❌ Mot de passe incorrect pour l'utilisateur : {username}")
                return None
                
        except User.DoesNotExist:
            logger.warning(f"❌ Utilisateur non trouvé : {username}")
            return None