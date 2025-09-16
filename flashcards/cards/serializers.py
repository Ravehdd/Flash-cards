from rest_framework import serializers
from .models import *
import re
from enum import Enum
from typing import Optional, Dict, Any
import json


class FlashcardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardSet
        fields = ['id', 'name', 'description', 'category', 'difficulty', 'is_public']
        read_only_fields = ['id', 'user']


class FlashcardSerializer(serializers.ModelSerializer):
    # Для отображения информации о наборе (только для чтения)
    flashcard_set_name = serializers.CharField(source='flashcard_set.name', read_only=True)

    # Для создания/обновления (только для записи)
    flashcard_set_id = serializers.PrimaryKeyRelatedField(
        queryset=FlashcardSet.objects.all(),
        write_only=True,
        source='flashcard_set'
    )

    class Meta:
        model = Flashcard
        fields = [
            'id',
            'word',
            'translation',
            'pinyin',
            'definition',
            'example_sentence',
            'audio_pronunciation',
            'hsk_level',
            'flashcard_set',  # для чтения (объект)
            'flashcard_set_id',  # для записи (ID)
            'flashcard_set_name',  # для чтения (название набора)
            'mastered',
            'created_date',
            'last_modified'
        ]
        read_only_fields = ['id', 'created_date', 'last_modified', 'flashcard_set', 'flashcard_set_name']

    def validate_word(self, value):
        """Валидация слова (китайские иероглифы)"""
        if not value.strip():
            raise serializers.ValidationError("Слово не может быть пустым")

        # Проверяем что слово содержит китайские иероглифы
        # Китайские иероглифы в Unicode: \u4e00-\u9fff
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if not chinese_pattern.search(value):
            raise serializers.ValidationError("Слово должно содержать китайские иероглифы")

        if len(value) > 50:
            raise serializers.ValidationError("Слово слишком длинное (максимум 50 символов)")

        return value.strip()

    # def validate_translation(self, value):
    #     """Валидация перевода"""
    #     if not value.strip():
    #         raise serializers.ValidationError("Перевод не может быть пустым")
    #
    #     if len(value) > 500:
    #         raise serializers.ValidationError("Перевод слишком длинный (максимум 500 символов)")
    #
    #     return value.strip()

    # def validate_pinyin(self, value):
    #     """Валидация пиньиня"""
    #     if value and value.strip():
    #         # Базовая проверка формата пиньиня
    #         pinyin_pattern = re.compile(r'^[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü\s]+$')
    #         if not pinyin_pattern.match(value):
    #             raise serializers.ValidationError("Пиньинь содержит недопустимые символы")
    #
    #         if len(value) > 100:
    #             raise serializers.ValidationError("Пиньинь слишком длинный (максимум 100 символов)")
    #
    #     return value.strip() if value else ''

    def validate_hsk_level(self, value):
        """Валидация уровня HSK"""
        if value is not None:
            if value not in range(1, 7):
                raise serializers.ValidationError("Уровень HSK должен быть от 1 до 6")
        return value

    # def validate_definition(self, value):
    #     """Валидация определения"""
    #     if value and len(value) > 2000:
    #         raise serializers.ValidationError("Определение слишком длинное (максимум 2000 символов)")
    #     return value.strip() if value else ''

    def validate_example_sentence(self, value):
        """Валидация примера предложения"""
        if value and len(value) > 1000:
            raise serializers.ValidationError("Пример предложения слишком длинный (максимум 1000 символов)")
        return value.strip() if value else ''

    def validate_flashcard_set_id(self, value):
        """Валидация что набор карточек существует и доступен"""
        if not FlashcardSet.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Набор карточек не существует")
        return value

    def validate(self, data):
        """Общая валидация"""
        # Проверяем что слово и перевод есть
        if not data.get('word') or not data.get('translation'):
            raise serializers.ValidationError("Слово и перевод обязательны")

        # Проверяем что пиньинь есть для китайских слов
        word = data.get('word', '')
        pinyin = data.get('pinyin', '')

        # Если есть китайские иероглифы, но нет пиньиня
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if chinese_pattern.search(word) and not pinyin.strip():
            raise serializers.ValidationError("Для китайских слов обязателен пиньинь")

        return data

    def create(self, validated_data):
        """Создание карточки с дополнительной логикой"""
        # Можно добавить дополнительную логику здесь
        # Например, автоматическое определение HSK уровня

        flashcard = Flashcard.objects.create(**validated_data)
        return flashcard

    def update(self, instance, validated_data):
        """Обновление карточки"""
        # Можно добавить логику отслеживания изменений
        instance = super().update(instance, validated_data)
        return instance


class WordSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    hsk_level = serializers.IntegerField(min_value=1, max_value=7)
    example = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
