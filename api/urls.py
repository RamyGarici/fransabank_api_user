from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from api import views
from django.conf import settings
from django.conf.urls.static import static

# Initialisation du routeur pour les vues basées sur les ViewSets
router = DefaultRouter()

# Enregistrement des ViewSets dans le routeur
router.register(r'demandecompte', views.DemandeCompteBancaireViewSet, basename='demandecompte')  # Pour les demandes de compte bancaire
router.register(r'client', views.ClientViewSet, basename='client')  # Pour les clients
router.register(r'employe', views.EmployeViewSet, basename='employe')  # Pour les employés

# Définition des URL patterns
urlpatterns = [
    # Route pour la connexion (JWT)
    path("login/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),

    # Route pour rafraîchir le token JWT
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Route pour l'inscription des utilisateurs
    path("register/", views.RegisterView.as_view(), name="register"),

    # Route pour obtenir les informations de l'utilisateur connecté
    path('infouser/', views.InfoUserView.as_view(), name='me'),

    # Inclusion des routes du routeur (demandecompte, client, employe)
    path("", include(router.urls)),

    # Route pour vérifier un token JWT
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Route pour la déconnexion
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Route pour vérifier l'email (lien envoyé par email)
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),

    # Route pour afficher une page après la vérification de l'email
    path('email-verified/', views.email_verified, name='email_verified'),

    # Route pour vérifier si un email est vérifié (utilisé par l'application mobile)
    path("api/check-email-verification/<str:email>/", views.check_email_verification),
]

# Ajout des routes pour les fichiers média en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)