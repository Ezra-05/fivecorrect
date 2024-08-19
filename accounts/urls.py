from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from django.contrib.auth.views import LogoutView
from .views import SignUpView

urlpatterns = [
    # User authentication
    path("signup/", views.signup, name="signup"),
    path('accounts/login/', views.signin, name='login'),
    path('accounts/logout/', views.signout, name='logout'),
]
