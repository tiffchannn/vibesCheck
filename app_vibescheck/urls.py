from django.urls import path
from . import views

urlpatterns= [
  path('', views.index),
  path('register', views.register),
  path('login', views.login),
  path('dashboard', views.dashboard),
  path('vibesCheck/newPlaylist', views.create_playlist),
  path('vibesCheck/playlist/<int:playlist_id>', views.playlist_info),
  path('vibesCheck/editPlaylist/<int:playlist_id>', views.edit_playlist),
  path('vibesCheck/newSong', views.create_song),
  path('vibesCheck/searchSong', views.search_song),
  path('vibesCheck/song/<int:song_id>', views.song_info),
  path('vibesCheck/editSong/<int:song_id>', views.edit_song),
  path('vibesCheck/likeSong/<int:song_id>', views.like_song),
  path('vibesCheck/removeSong/<int:playlist_id>', views.remove_song_from_playlist),
  path('vibesCheck/addToPlaylist/<int:playlist_id>', views.add_song_to_playlist),
  path('logout', views.logout)
]

