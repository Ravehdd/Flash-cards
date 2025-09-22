from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import FlashcardSet, Category, Flashcard
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from pypinyin import pinyin, Style
import requests

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test(request):
    return Response({"ok": "ok"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

        print(request.user.id)

        # Создаем набор карточек
        flashcard_set = FlashcardSet.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            category=category,
            difficulty=data.get('difficulty', 'beginner'),
            is_public=data.get('is_public', False),
            user=request.user  # Текущий пользователь
        )

        # Сериализуем и возвращаем ответ
        serializer = FlashcardSetSerializer(flashcard_set)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CreateFlashcardAPIView(APIView):
    def get_translation(self, word, destination_language_code):
        url = f'https://ftapi.pythonanywhere.com/translate'

        # Минимальные необходимые headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }

        params = {
            'sl': "zh-cn",
            'dl': destination_language_code,
            'text': word
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            # print(f"Status: {response.status_code}")
            # print(f"Response: {response.text[:200]}...")

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error: {e}")
            return None

    def post(self, request):
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            print("Validated data:", validated_data)
            print("Flashcard set object:", validated_data.get("flashcard_set"))
            print("Flashcard set ID:",
                  validated_data.get("flashcard_set").id if validated_data.get("flashcard_set") else None)

            translation_data = self.get_translation(validated_data["word"], validated_data["dl"])

            translation = validated_data["translation"] or translation_data["translations"]["possible-translations"]
            pinyin = translation_data["pronunciation"]["source-text-phonetic"]

            card = Flashcard.objects.create(
                word=validated_data["word"],
                translation=translation,
                pinyin=pinyin,
                definition=validated_data["definition"],
                example_sentence=validated_data["example_sentence"],
                hsk_level=validated_data["hsk_level"],
                flashcard_set=validated_data["flashcard_set"]  # Используем объект из validated_data
            )

            return Response({
                "id": card.id,
                "word": card.word,
                "pinyin": card.pinyin,
                "translation": card.translation,
                "definition": card.definition,
                "example_sentence": card.example_sentence,
                "flashcard_set_id": card.flashcard_set.id
            })

        print("Serializer errors:", serializer.errors)
        return Response({"error": serializer.errors})

class UserFlashcardSetsView(generics.ListAPIView):
    serializer_class = UserFlashcardSetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Простая версия без аннотации
        return FlashcardSet.objects.filter(
            user=self.request.user
        ).order_by('-creation_date')


class FlashcardCreateView(generics.CreateAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
