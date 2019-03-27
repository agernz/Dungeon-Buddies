from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='game-index'),
    path('guild/', views.guild, name='game-guild'),
    path('guild-create/', views.createGuild, name='game-guild-create'),
]
