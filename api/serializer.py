from api.models import User, Profile, DemandeCompteBancaire, Client, Employe, Document, TypeDocument
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from api.utils import send_verification_email

# Sérialiseur pour l'utilisateur (User)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_mobile_user')

# Sérialiseur pour l'employé (Employe)
class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ('id', 'username', 'email', 'role')

# Sérialiseur pour le token JWT (MyTokenObtainPairSerializer)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des informations supplémentaires au token
        token['first_name'] = user.profile.first_name
        token['last_name'] = user.profile.last_name
        token['username'] = user.username
        token['email'] = user.email
        token['verified'] = user.profile.verified

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['email_verified'] = self.user.profile.verified

        # Vérifier si l'email est vérifié
        if not user.profile.verified:
            raise serializers.ValidationError("Vous devez vérifier votre adresse email avant de vous connecter.")

        return data

# Sérialiseur pour l'inscription (RegisterSerializer)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        # Vérifier que les mots de passe correspondent
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        # Supprimer le champ password2 avant de créer l'utilisateur
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        # Hasher le mot de passe et sauvegarder l'utilisateur
        user.set_password(validated_data['password'])
        user.save()
        # Envoyer un email de vérification
        send_verification_email(user)
        return user

# Sérialiseur pour la demande de compte bancaire (DemandeCompteBancaire)
class DemandeCompteBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeCompteBancaire
        fields = '__all__'
        extra_kwargs = {
            "user": {"read_only": True}  # L'utilisateur est automatiquement assigné
        }

    def validate(self, data):
        user = self.context['request'].user
        # Vérifier si l'utilisateur a déjà une demande en cours
        if DemandeCompteBancaire.objects.filter(user=user, status__in=['pending', 'approved']).exists():
            raise serializers.ValidationError("Vous avez déjà une demande en cours.")
        return data

# Sérialiseur pour le client (Client)
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

# Sérialiseur pour le document (Document)
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

# Sérialiseur pour le type de document (TypeDocument)
class TypeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeDocument
        fields = '__all__'

# Sérialiseur pour le profil (Profile)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'