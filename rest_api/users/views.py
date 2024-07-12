# users/views.py
from rest_framework import status, generics,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Arcticle
from .serializers import UserLoginSerializer, ArcticleSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        if not user.is_active:
            return Response({'detail': 'Inactive user'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
class ArcticleViewSet(viewsets.ModelViewSet):
    queryset = Arcticle.objects.all()
    serializer_class = ArcticleSerializer
    permission_classes = [
        IsAuthenticated
    ]
        