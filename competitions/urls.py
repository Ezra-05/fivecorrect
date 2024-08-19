from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    path('', views.competition_list, name='competition_list'),
    path('<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('<int:competition_id>/results/', views.calculate_results, name='calculate_results'),
    path('leaderboard/<int:competition_id>/', views.leaderboard, name='leaderboard'),
    path('match/<int:match_id>/predict/', views.make_prediction, name='make_prediction'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),  # Updated to use username
]


