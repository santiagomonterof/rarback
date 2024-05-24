from django.contrib.auth.models import User
from django.db import models


class ParticipatingUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raffle = models.ForeignKey('Raffle', on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100)
    winner = models.BooleanField(default=False)
