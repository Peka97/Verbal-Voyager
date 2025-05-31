from django.urls import path

from .views import LessonPageView, ExerciseConstructorCreateView, WordAutocompleteView

urlpatterns = [
    path('<int:lesson_page_id>/', LessonPageView.as_view(), name='lesson_page'),
    path('create/', ExerciseConstructorCreateView.as_view(),
         name='constructor_create'),
    path('word-autocomplete/', WordAutocompleteView.as_view(),
         name='word_autocomplete'),
]
