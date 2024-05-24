from rest_framework import serializers, viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.response import Response

import raffles.api
from raffles.api import UserSerializer
from raffles.models import Raffle, ParticipatingUser


class RaffleSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='created_by',
        write_only=True
    )

    class Meta:
        model = Raffle
        fields = '__all__'


class RaffleViewSet(viewsets.ModelViewSet):
    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer

    @action(detail=False, methods=['post'], url_path='actives')
    def actives(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'user_id': 'This field is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        active_raffles = Raffle.objects.filter(status=1)
        active_raffles = active_raffles.exclude(created_by=user_id)
        serializer = RaffleSerializer(active_raffles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='participate')
    def participate(self, request, pk=None):
        raffle = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'user_id': 'This field is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if raffle.users.filter(id=user_id).exists():
            return Response({'error': 'El usuario ya se unio a la rifa.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if raffle.users.count() >= raffle.ticket_amount:
            return Response({'error': 'La rifa ya esta llena.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=user_id)
        ParticipatingUser.objects.create(
            user_id=user.id,
            raffle_id=raffle.id,
            ticket_number=raffle.ticket_code + "-" + str(raffle.users.count() + 1)
        )
        raffle.save()
        return Response(RaffleSerializer(raffle).data)

    @action(detail=True, methods=['get'], url_path='participating')
    def participating(self, request, pk=None):
        raffle = self.get_object()
        participating_users = ParticipatingUser.objects.filter(raffle=raffle)
        serializer = raffles.api.ParticipatingUserSerializer(participating_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        raffle = self.get_object()
        raffle.status = -1
        raffle.save()
        return Response(RaffleSerializer(raffle).data)

    @action(detail=True, methods=['post'], url_path='finish')
    def finish(self, request, pk=None):
        raffle = self.get_object()
        raffle.status = 0
        raffle.save()
        return Response(RaffleSerializer(raffle).data)

    @action(detail=True, methods=['get'], url_path='winners')
    def winners(self, request, pk=None):
        raffle = self.get_object()
        participating_users = ParticipatingUser.objects.filter(raffle=raffle, winner=True)
        serializer = raffles.api.ParticipatingUserSerializer(participating_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='draw')
    def draw(self, request, pk=None):
        raffle = self.get_object()
        participating_users = ParticipatingUser.objects.filter(raffle=raffle, winner=False)
        if raffle.status != -1:
            return Response({'error': 'La rifa no esta en estado de sorteo.'},
                            status=status.HTTP_400_BAD_REQUEST)
        winner = participating_users.order_by('?').first()
        winner.winner = True
        winner.save()
        serializer = raffles.api.ParticipatingUserSerializer(winner)
        return Response(serializer.data)
