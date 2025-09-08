from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class FlashcardSet(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название набора")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(  # Внешний ключ вместо CharField
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        verbose_name="Сложность"
    )
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_public = models.BooleanField(default=False, verbose_name="Публичный набор")
    total_cards = models.IntegerField(default=0, verbose_name="Всего карточек")
    still_learning = models.IntegerField(default=0, verbose_name="Изучается")
    mastered = models.IntegerField(default=0, verbose_name="Изучено")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flashcard_sets',
        verbose_name="Пользователь"
    )

    class Meta:
        ordering = ['-creation_date']
        verbose_name = "Набор карточек"
        verbose_name_plural = "Наборы карточек"

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def update_stats(self):
        """Автоматическое обновление статистики"""
        cards = self.flashcards.all()
        self.total_cards = cards.count()
        self.still_learning = cards.filter(mastered=False).count()
        self.mastered = cards.filter(mastered=True).count()
        self.save()


class Flashcard(models.Model):
    word = models.CharField(max_length=200, verbose_name="Слово (汉字)")
    translation = models.CharField(max_length=500, verbose_name="Перевод")
    pinyin = models.CharField(max_length=200, verbose_name="Пиньинь")
    definition = models.TextField(blank=True, verbose_name="Определение")
    example_sentence = models.TextField(blank=True, verbose_name="Пример предложения")
    audio_pronunciation = models.FileField(
        upload_to='flashcard_audio/',
        null=True,
        blank=True,
        verbose_name="Аудио произношение"
    )
    hsk_level = models.IntegerField(
        choices=[(i, f'HSK {i}') for i in range(1, 7)],
        null=True,
        blank=True,
        verbose_name="Уровень HSK"
    )
    flashcard_set = models.ForeignKey(
        FlashcardSet,
        on_delete=models.CASCADE,
        related_name='flashcards',
        verbose_name="Набор карточек"
    )
    mastered = models.BooleanField(default=False, verbose_name="Изучено")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение")

    class Meta:
        ordering = ['created_date']
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        indexes = [
            models.Index(fields=['word', 'pinyin']),
            models.Index(fields=['hsk_level']),
        ]

    def __str__(self):
        return f"{self.word} - {self.translation}"

    def save(self, *args, **kwargs):
        # Сначала сохраняем карточку
        super().save(*args, **kwargs)
        # Затем обновляем статистику набора
        self.flashcard_set.update_stats()

    def delete(self, *args, **kwargs):
        # Запоминаем набор перед удалением
        flashcard_set = self.flashcard_set
        # Удаляем карточку
        super().delete(*args, **kwargs)
        # Обновляем статистику набора
        flashcard_set.update_stats()