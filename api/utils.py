from django.core.mail import send_mail
from django.conf import settings
from api.models import EmailVerificationToken



def send_verification_email(user):
        token,created=EmailVerificationToken.objects.get_or_create(user=user)
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{token.token}/"
        send_mail(
        "Vérifiez votre adresse email",
        f"Cliquez sur le lien suivant pour vérifier votre email : {verification_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
