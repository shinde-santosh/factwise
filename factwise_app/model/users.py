from django.db import models
from .base import Base


class User(Base):
    ''' Model Fields '''

    # Fields
    name = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=128)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name
