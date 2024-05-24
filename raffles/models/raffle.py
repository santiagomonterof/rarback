from django.contrib.auth.models import User
from django.db import models


class Raffle(models.Model):
    name = models.CharField(max_length=255)
    ticket_amount = models.IntegerField()
    ticket_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_ACTIVE = 1
    STATUS_DRAWN = 0
    STATUS_IN_DRAW = -1
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_DRAWN, "Drawn"),
        (STATUS_IN_DRAW, "In Draw"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by')
    users = models.ManyToManyField(User, through='ParticipatingUser', related_name='raffles')
