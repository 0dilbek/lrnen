from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('vocabulary/', views.VocabularyListView.as_view(), name='vocabulary_list'),
    path('vocabulary/<int:pk>/', views.VocabularyDetailView.as_view(), name='vocabulary_detail'),
    path('progress/', views.UserProgressView.as_view(), name='user_progress'),
    path('stats/', views.StatsView.as_view(), name='stats'),
]
