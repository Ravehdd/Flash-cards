from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import FlashcardSet, Category, Flashcard
from .serializers import FlashcardSetSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_flashcard_set(request):
    """
    Создание нового набора карточек
    """
    try:
        # Извлекаем данные из запроса
        data = request.data

        # Проверяем обязательные поля
        if 'name' not in data:
            return Response(
                {'error': 'Название набора обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обрабатываем категорию
        category = None
        if 'category' in data:
            category_name = data['category']
            category, created = Category.objects.get_or_create(name=category_name)

        user = User.objects.get(id=request.data["user"])

        # Создаем набор карточек
        flashcard_set = FlashcardSet.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            category=category,
            difficulty=data.get('difficulty', 'beginner'),
            is_public=data.get('is_public', False),
            user=user  # Текущий пользователь
        )

        # Сериализуем и возвращаем ответ
        serializer = FlashcardSetSerializer(flashcard_set)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )