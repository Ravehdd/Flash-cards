from rest_framework import serializers
from .models import FlashcardSet


class FlashcardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardSet
        fields = ['id', 'name', 'description', 'category', 'difficulty', 'is_public']
        read_only_fields = ['id', 'user']