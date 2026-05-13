from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('submit/', views.QuizSubmitView.as_view(), name='quiz_submit'),
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/submit/', views.ExerciseSubmitView.as_view(), name='exercise_submit'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('attempts/', views.QuizAttemptListView.as_view(), name='quiz_attempts'),
    path('exercise-attempts/', views.ExerciseAttemptListView.as_view(), name='exercise_attempts'),
]
