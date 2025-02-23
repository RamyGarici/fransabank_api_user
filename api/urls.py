from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView
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
    path('infouser/', views.InfoUserView.as_view(), name='me'), 
    path("", include(router.urls)), 
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
