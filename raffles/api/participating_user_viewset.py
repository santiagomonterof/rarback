from rest_framework import serializers, viewsets

from raffles.api import UserSerializer
from raffles.models import ParticipatingUser


class ParticipatingUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=ParticipatingUser.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = ParticipatingUser
        fields = '__all__'


class ParticipatingUserViewSet(viewsets.ModelViewSet):
    queryset = ParticipatingUser.objects.all()
    serializer_class = ParticipatingUserSerializer
