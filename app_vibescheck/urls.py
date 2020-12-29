from django.urls import path
from . import views

urlpatterns= [
  path('', views.index),
  path('register', views.register),
  path('login', views.login),
  path('logout', views.logout),
  path('playlist/new', views.playlist_new),
  path('playlist/<int:playlist_id>', views.playlist_id),
  path('playlist/<int:playlist_id>/edit', views.playlist_id_edit),
  path('playlist/<int:playlist_id>/song/<int:song_id>/toggle', views.playlist_id_song_id_toggle),
  path('song/new', views.song_new),
  path('song/search', views.song_search),
  path('song/<int:song_id>', views.song_id),
  path('song/<int:song_id>/edit', views.song_id_edit),
  path('song/<int:song_id>/like', views.song_id_like),
]

