from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('student-groups/', views.StudentGroupListView.as_view(), name='student_group_list'),
    path('student-groups/<int:pk>/', views.StudentGroupDetailView.as_view(), name='student_group_detail'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]
