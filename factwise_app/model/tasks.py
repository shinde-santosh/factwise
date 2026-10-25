from django.db import models
from .base import Base
from ..model.boards import Board
from ..model.users import User
from utility.constants import STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_COMPLETE


class Task(Base):
    ''' Model Fields '''

    # Fields
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True, default="")

    STATUS_CHOICES = ((STATUS_OPEN, 'Open'), (STATUS_IN_PROGRESS, 'In progress'), (STATUS_COMPLETE, 'Complete'))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)

    # Relationships
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        db_table = "tasks"
        unique_together = ("board", "title")

    def __str__(self):
        return self.title
