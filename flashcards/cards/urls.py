from django.urls import path, re_path, include
from .views import *
urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api/sets/create/', create_flashcard_set, name='create-set'),
]
