from django.db import models
from .base import Base
from ..model.teams import Team
from utility.constants import STATUS_OPEN, STATUS_CLOSED


class Board(Base):
    ''' Model Fields '''

    # Fields
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True, default="")
    end_time = models.DateTimeField(null=True, blank=True)

    STATUS_CHOICES = ((STATUS_OPEN, 'Open'), (STATUS_CLOSED, 'Closed'))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)

    # Relationships
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="boards")

    class Meta:
        db_table = "boards"
        unique_together = ("team", "name")

    def __str__(self):
        return self.name
