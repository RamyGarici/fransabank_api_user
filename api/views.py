from django.shortcuts import render
from api.models import User, Profile,Client,DemandeCompteBancaire,EmailVerificationToken
from api.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer,ClientSerializer,DemandeCompteBancaireSerializer
from rest_framework.decorators import api_view,action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DemandeCompteBancaire, Document, TypeDocument
from django.http import JsonResponse,HttpResponse
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login

from datetime import datetime


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer  

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]  
    serializer_class = RegisterSerializer
class InfoUserView(APIView):
    permission_classes = [IsAuthenticated]  # Seul un user connecté peut accéder

    def get(self, request):
        serializer = UserSerializer(request.user)  # Sérialiser l'utilisateur connecté
        return Response(serializer.data)  # Retourner ses infos

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        request.user.auth_token.delete()
        return Response({"message":"Deconnexion reussie"},status=200)


class DemandeCompteBancaireViewSet(viewsets.ModelViewSet):
    serializer_class = DemandeCompteBancaireSerializer
    permission_classes = [IsAuthenticated]
    queryset = DemandeCompteBancaire.objects.all()
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DemandeCompteBancaire.objects.all()
        return DemandeCompteBancaire.objects.filter(user=user) 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approuver(self, request, pk=None):
        
        demande = self.get_object()
        if demande.status == 'approved':
            return Response({"message": "Cette demande est déjà approuvée."}, status=400)

        demande.status = 'approved'
        demande.save()  
        
        return Response({"message": "Demande approuvée et client créé."})
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def rejeter(self, request, pk=None):
        
        demande = self.get_object()
        if demande.status == 'rejected':
            return Response({"message": "Cette demande est déjà rejetée."}, status=400)

        demande.status = 'rejected'
        demande.save()  
        
        return Response({"message": "Demande rejetée ."})
    
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        demande = self.get_object()
        type_document_id = request.POST.get('type_document_id')
        type_document = TypeDocument.objects.filter(type_document_id=type_document_id).first()
        
        existing_document = Document.objects.filter(
        user=request.user, demande=demande, type_document=type_document).exists()


        if not type_document:
            return Response({'error': 'Type de document non valide'}, status=400)
        
        
        if existing_document:
          return Response({'status': False, 'error': 'Ce document a déjà été envoyé.'}, status=400)


        document = Document(
            user=request.user,  # Associer le client
            demande=demande,  # Associer la demande de compte
            type_document=type_document,  # Spécifier le type de document
            fichier=request.FILES['document']
        )

        #pour verifier que on upload pas un document vide
        if not document.fichier:
          return Response({'status': False, 'error': 'Aucun fichier fourni.'}, status=400)
        document.save()
#ajouter status true or false
#ajouter if pour tester le document s envoie qu une seule fois
        return Response({'stat':True ,'message': 'Document ajouté avec succès !', 'document_url': document.fichier.url})



class ClientViewSet(viewsets.ModelViewSet):  
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        user = self.request.user  
        
       
        if user.is_staff:
            return Client.objects.all()

  
        return Client.objects.filter(user=user)




def verify_email(request, token):
    verification_token = get_object_or_404(EmailVerificationToken, token=token)

    # Vérifier si le token a expiré
    if verification_token.is_expired():
        verification_token.delete()
        return JsonResponse({"error": "Le lien de vérification a expiré. Demandez un nouvel email."}, status=400)

    # Activer le compte de l'utilisateur
    user = verification_token.user
    user.profile.verified = True
    user.is_active = True  # ✅ Autorise la connexion
    user.profile.save()
    user.save()
    
    # Supprimer le token après vérification
    verification_token.delete()

    # Retourner une réponse JSON pour Flutter
    return render(request, "email_verified.html")


   
class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if not request.user.profile.verified and request.path != reverse("api/verify-email"):
                return redirect("api/verify-email")

        return self.get_response(request)
def email_verified(request):
    return render(request, 'email_verified.html')

def check_email_verification(request, email):
    try:
        user = User.objects.get(email=email)
        return JsonResponse({'is_verified': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'error': "Utilisateur non trouvé"}, status=404)
