from django.shortcuts import render
from api.models import User, Profile,Client,DemandeCompteBancaire
from api.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer,ClientSerializer,DemandeCompteBancaireSerializer
from rest_framework.decorators import api_view,action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DemandeCompteBancaire, Document, TypeDocument
from django.http import JsonResponse

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
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        demande = self.get_object()
        type_document_id = request.POST.get('type_document_id')
        type_document = TypeDocument.objects.filter(type_document_id=type_document_id).first()

        if not type_document:
            return Response({'error': 'Type de document non valide'}, status=400)

        document = Document(
            user=request.user,  # Associer le client
            demande=demande,  # Associer la demande de compte
            type_document=type_document,  # Spécifier le type de document
            fichier=request.FILES['document']
        )
        document.save()

        return Response({'message': 'Document ajouté avec succès !', 'document_url': document.fichier.url})



class ClientViewSet(viewsets.ReadOnlyModelViewSet):  
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        user = self.request.user  
        
       
        if user.is_staff:
            return Client.objects.all()

  
        return Client.objects.filter(user=user)
    
