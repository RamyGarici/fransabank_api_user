from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from api import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'demandecompte', views.DemandeCompteBancaireViewSet, basename='demandecompte')
router.register(r'client', views.ClientViewSet, basename='client')

urlpatterns = [
    path("login/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("infouser/", views.InfoUserView.as_view(), name="me"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("email_verified/", views.email_verified, name="email_verified"),
    path("check-email-verification/<str:email>/", views.check_email_verification, name="check_email_verification"),
    path("api/", include(router.urls)),  # API versionnée proprement
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

# Servir les fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
