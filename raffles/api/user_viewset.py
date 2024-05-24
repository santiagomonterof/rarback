from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from raffles.models import Raffle
import raffles.api
from raffles.models.profile import Profile


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='profile.phone')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})

        username = validated_data.get('username')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        password = validated_data.pop('password')
        hashed_password = make_password(password)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password
        )

        Profile.objects.create(user=user, phone=profile_data['phone'])

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        phone = profile_data.get('phone')

        instance = super().update(instance, validated_data)

        profile = instance.profile
        if phone:
            profile.phone = phone
            profile.save()

        return instance


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me', url_name='me')
    def get_user_info(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='raffles/created')
    def raffles_created(self, request, pk=None):
        user = self.get_object()
        user_raffles = Raffle.objects.filter(created_by=user)
        serializer = raffles.api.RaffleSerializer(user_raffles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='raffles/participating')
    def raffles_participating(self, request, pk=None):
        user = self.get_object()
        user_raffles = user.raffles.all()
        serializer = raffles.api.RaffleSerializer(user_raffles, many=True)
        return Response(serializer.data)
