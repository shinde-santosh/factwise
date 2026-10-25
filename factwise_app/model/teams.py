from django.db import models
from .base import Base
from ..model.users import User


class Team(Base):
    ''' Model Fields '''

    # Fields
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128, blank=True, default="")

    # Relationships
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_teams")
    users = models.ManyToManyField(User, blank=True, related_name="teams")

    class Meta:
        db_table = "teams"

    def __str__(self):
        return self.name
