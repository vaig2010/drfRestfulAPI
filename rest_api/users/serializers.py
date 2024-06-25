# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, Arcticle

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ArcticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arcticle
        fields = ['title', 'content', 'author']