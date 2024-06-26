# users/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Arcticle
from .serializers import UserSerializer, UserLoginSerializer, ArcticleSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = CustomUser.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({'detail': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        

class ArcticleAPIView(ListCreateAPIView):
    queryset = Arcticle.objects.all()
    serializer_class = ArcticleSerializer
    def get(self, request):
        articles = self.get_queryset()
        serializer = self.get_serializer(articles, many=True)
        return Response({"posts": serializer.data})
    
    def post(self, request):
        serializer = ArcticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            if isinstance(user, SimpleLazyObject):
                user = CustomUser.objects.filter(id=user.id).first()
        serializer.save(author=user)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return Response({"error": "Method PUT not allowed"})
        try:
            instance = Arcticle.objects.get(pk=pk)
        except Arcticle.DoesNotExist:
            return Response({"error": "Object does not exist"})
        serializer = ArcticleSerializer(data=request.data, instance=instance)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)