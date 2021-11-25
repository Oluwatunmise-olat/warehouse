from django.urls import path
from user_control import views

app_name = "user_control"

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('change-password/', views.ChangePasswordView.as_view()),
]