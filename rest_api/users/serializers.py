# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, Arcticle, ReferralCode

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ArcticleSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Arcticle
        fields = ['title', 'content', 'author']
        

class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['code', 'expiration_date']
