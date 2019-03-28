from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='game-index'),
    path('guild/', views.guildPage, name='game-guild'),
    path('guild-create/', views.createGuild, name='game-guild-create'),
    path('guild-join/', views.joinGuild, name='game-guild-join'),
]
