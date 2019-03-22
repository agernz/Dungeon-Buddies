from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='game-index'),
    path('guild/', views.guild, name='game-guild'),
]
