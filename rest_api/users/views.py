# users/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Arcticle
from .serializers import UserSerializer, UserLoginSerializer, ArcticleSerializer
from rest_framework import permissions
from rest_framework import generics, viewsets
from django.contrib.auth import get_user_model

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
  
class ArcticleViewSet(viewsets.ModelViewSet):
    queryset = Arcticle.objects.all()
    serializer_class = ArcticleSerializer
        