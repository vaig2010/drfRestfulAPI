# users/views.py
import uuid
from rest_framework import status, generics,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Arcticle, ReferralCode
from .serializers import (UserLoginSerializer, ArcticleSerializer,
                          UserSerializer, UserRegistrationSerializer,
                          ReferralCodeSerializer)
from django.contrib.auth.models import User
from django.utils import timezone
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
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
    permission_classes = [IsAuthenticated]

class ReferralCodeViewSet(viewsets.ModelViewSet):
    queryset = ReferralCode.objects.all()
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter queryset to only show ReferralCodes of the authenticated user
        user = self.request.user
        return ReferralCode.objects.filter(user=user)
    def generate_unique_code(self):
        while True:
            code = str(uuid.uuid4()).replace("-", "")[:20]
            if not ReferralCode.objects.filter(code=code).exists():
                return code

    def perform_create(self, serializer):
        user = self.request.user
        # Generate unique code
        code = self.generate_unique_code()
        # Set expiration date to 30 days from now
        expiration_date = timezone.now() + timezone.timedelta(days=30)
        # Create the referral code instance
        serializer.save(user=user, code=code, expiration_date=expiration_date)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the instance belongs to the authenticated user
        if instance.user != request.user:
            return Response({"error": "You do not have permission to delete this referral code."},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({"message": "Referral code deleted successfully.","code": instance.code}, status=status.HTTP_204_NO_CONTENT)
    
        