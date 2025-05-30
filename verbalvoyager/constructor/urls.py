from django.urls import path

from .views import ExerciseView, ExerciseConstructorCreateView, WordAutocompleteView

urlpatterns = [
    path('<int:exercise_id>/', ExerciseView.as_view(), name='exercise'),
    path('create/', ExerciseConstructorCreateView.as_view(),
         name='constructor_create'),
    path('word-autocomplete/', WordAutocompleteView.as_view(),
         name='word_autocomplete'),
]
