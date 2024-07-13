import uuid
from rest_framework import serializers
from .models import  Arcticle, ReferralCode
from django.contrib.auth.models import User
from django.utils import timezone
# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()
            if user and user.check_password(password):
                return user
            else:
                raise serializers.ValidationError('Invalid Credentials')
        else:
            raise serializers.ValidationError('Must include "username" and "password"')
        
class ArcticleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Arcticle
        fields = ['id', 'title', 'content']
        

class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['code', 'expiration_date']
        read_only_fields = ['code', 'expiration_date']
    
    def validate(self, attrs):
        user = self.context['request'].user
        # Check if the user already has a ReferralCode
        existing_code = ReferralCode.objects.filter(user=user).first()
        if existing_code:
            raise serializers.ValidationError("User already has a ReferralCode")
        return attrs
        


