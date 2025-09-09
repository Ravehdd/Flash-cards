from django.contrib import admin
from .models import Category, FlashcardSet, Flashcard


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(FlashcardSet)
class FlashcardSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'difficulty', 'total_cards']
    list_filter = ['category', 'difficulty', 'is_public']
    search_fields = ['name', 'user__username']


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'pinyin', 'hsk_level', 'mastered']
    list_filter = ['hsk_level', 'mastered', 'flashcard_set']
    search_fields = ['word', 'translation']