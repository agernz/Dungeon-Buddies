from django.urls import path
from register import views as register_views
from game import views as game_views

urlpatterns = [
    path('', game_views.index, name='game-index'),
    path('register/', register_views.index, name='register-index'),
    path('login/', register_views.loginUser, name='register-login'),
]
