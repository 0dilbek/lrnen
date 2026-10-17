from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('submit/', views.QuizSubmitView.as_view(), name='quiz_submit'),
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('assets/', views.ExerciseAssetLibraryView.as_view(), name='exercise_assets'),
    path('exercises/submit/', views.ExerciseSubmitView.as_view(), name='exercise_submit'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('attempts/', views.QuizAttemptListView.as_view(), name='quiz_attempts'),
    path('exercise-attempts/', views.ExerciseAttemptListView.as_view(), name='exercise_attempts'),
    path('notifications/', views.AdminNotificationListView.as_view(), name='admin_notifications'),
    path('notifications/read-all/', views.AdminNotificationReadAllView.as_view(), name='admin_notifications_read_all'),
    path('notifications/<int:pk>/', views.AdminNotificationDetailView.as_view(), name='admin_notification_detail'),
]
