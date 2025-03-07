from django.core.mail import send_mail
from django.conf import settings
from api.models import EmailVerificationToken

def send_verification_email(user):
    # Générer ou récupérer un token existant
    token, created = EmailVerificationToken.objects.get_or_create(user=user)
    
    # Définir le lien de vérification (choisir selon besoin)
    if hasattr(settings, "FRONTEND_URL"):  # Si tu veux que Flutter gère la vérification
        verification_link = f"{settings.FRONTEND_URL}/api/verify-email/{token.token}/"
    else:  # Si Django gère directement la vérification
        verification_link = f"http://127.0.0.1:8000/api/verify-email/{token.token}/"

    # Envoyer l'email
    send_mail(
        subject="Vérifiez votre adresse email",
        message=f"Cliquez sur le lien suivant pour vérifier votre email : {verification_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
