from django.urls import path, re_path, include
from .views import *
urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api/sets/create/', create_flashcard_set, name='create-set'),
    # path("test/", test)
    path("api/flashcard/create/", FlashcardCreateView.as_view()),
    path("api/flashcard/create/2/", CreateFlashcardAPIView.as_view()),
    path("api/sets/get/", UserFlashcardSetsView.as_view())
]
