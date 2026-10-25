from rest_framework import serializers
from ..models import Board

class BoardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = "__all__"
