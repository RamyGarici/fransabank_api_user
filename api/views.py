from django.shortcuts import render
from api.models import User, Profile,Client,DemandeCompteBancaire
from api.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer,ClientSerializer,DemandeCompteBancaireSerializer
from rest_framework.decorators import api_view,action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

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




class DemandeCompteBancaireViewSet(viewsets.ModelViewSet):
    serializer_class = DemandeCompteBancaireSerializer
    permission_classes = [IsAuthenticated]

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


class ClientViewSet(viewsets.ReadOnlyModelViewSet):  
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        user = self.request.user  
        
       
        if user.is_staff:
            return Client.objects.all()

  
        return Client.objects.filter(user=user)