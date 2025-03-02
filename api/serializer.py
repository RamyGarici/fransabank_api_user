from api.models import User,Profile,DemandeCompteBancaire,Client
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from api.utils import send_verification_email  



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['first_name'] = user.profile.first_name
        token['last_name'] = user.profile.last_name
        token['username'] = user.username
        token['email'] = user.email
        token['verified'] = user.profile.verified  

        return token


    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user  # L'utilisateur authentifié
        data['email_verified'] = self.user.profile.verified
        print(f"🔍 Email vérifié pour {self.user.email} : {self.user.profile.verified}")

        if not user.profile.verified:
            raise serializers.ValidationError("Vous devez vérifier votre adresse email avant de vous connecter.")

        return data




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)  # Ajout de first_name
    last_name = serializers.CharField(write_only=True, required=True)   # Ajout de last_name

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')  # Inclure first_name et last_name

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Enlever password2 qui n'est pas nécessaire pour la création de l'utilisateur
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],  # Assigner first_name
            last_name=validated_data['last_name'],    # Assigner last_name
        )
        user.set_password(validated_data['password'])  # Hash du mot de passe
        user.save()  # Sauvegarder l'utilisateur
        send_verification_email(user)
        return user

 

class DemandeCompteBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeCompteBancaire
        fields = '__all__'
        extra_kwargs = {
           "user": {"read_only": True}}

    def validate(self, data):
        user = self.context['request'].user
        if DemandeCompteBancaire.objects.filter(user=user, status__in=['pending', 'approved']).exists():
            raise serializers.ValidationError("Vous avez déjà une demande en cours.")
        return data


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client  
        fields = '__all__' 
    