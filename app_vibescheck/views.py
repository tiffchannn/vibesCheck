from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import bcrypt
from datetime import date

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys


def register(request):
    if request.method == 'POST':
        errors = User.objects.validate_registration(request.POST)

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            form_password = request.POST['password']
            pw_hash = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt()).decode()

            user = User.objects.create(
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                birthday = request.POST['birthday'],
                password = pw_hash
                )

            request.session['user_id'] = user.id
            messages.success(request, "Registration was successful, please login!")

    # return redirect('/')
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        errors = User.objects.validate_login(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            user = User.objects.get(email=request.POST['login_email'])
            request.session['user_id'] = user.id

    return redirect('/')

def logout(request):

    request.session.clear()
    # messages.success(request, "Logout was successful, until next time!")
    return redirect('/')

def index(request):
    if 'user_id' not in request.session:
        # messages.error(request, "Please log in!")
        return render(request, 'index.html')

    user = User.objects.get(id=request.session['user_id'])
    liked_songs = user.liked_songs.all()

    # TODO: Make showing liked songs less expensive
    context = {
        "user": user,
        "all_playlists": Playlist.objects.all(),
        "all_songs": Song.objects.all(),
        "liked_songs": liked_songs # user's liked songs
    }
    # when successfully registered, redirect back to login/register page & login
    return render(request, 'home.html', context)

def song_new(request):
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        return render(request, 'song_new.html')

    elif request.method == 'POST':

        errors = Song.objects.validate_song(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/song/new')
        else:
            song = Song.objects.create(title=request.POST['title'], artist=request.POST['artist'])

            return redirect('/')

    return redirect('/')

def song_search(request):
    SETTINGS = {
        "client_id": "cf3e3d623cae428987e52a41c5f9ad8a",
        "client_secret": "522fb8f9cc734d4f9b3c62c39cd19c1f",
        "search_limit": 5
    }
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SETTINGS['client_id'],client_secret=SETTINGS['client_secret']))
        results = sp.search(request.POST['title'], limit = SETTINGS['search_limit'])

        # Loop through spotify search results and create list of song objects
        songs = []
        search_results = []
        for result in results['tracks']['items']:
            song = {
                "title": "",
                "artist": "",
                "image_url": ""
            }
            song['title'] = result['name']
            song['image_url'] = result['album']['images'][1]['url']

            song_artists_list = []
            for artist in result['artists']:
                song_artists_list.append(artist['name'])
            song['artist'] = ", ".join(song_artists_list)
            search_results.append(song)

            # take search results and add info into db as new song
            errors = Song.objects.validate_song(song)
            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
            else:
                song = Song.objects.create(title=song['title'], artist=song['artist'], image_url=song['image_url'])
                songs.append(song)


        context = {
            "user": user,
            "all_playlists": Playlist.objects.all(),
            "all_songs": Song.objects.all(),
            "liked_songs": user.liked_songs.all(), # user's liked songs
            "songs": songs # list of songs that were added from the search bar
        }

        return render(request, 'song_new.html', context)

def song_id(request, song_id):

    song = Song.objects.get(id=song_id)
    user = User.objects.get(id=request.session['user_id'])

    context = {
        'song': song,
        'user': user,
        'liked_songs': user.liked_songs.all()
    }
    return render(request, 'song_id.html', context)

def song_id_edit(request, song_id):

    song = Song.objects.get(id=song_id)
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        context={
            'song': song,
            'user': user
        }
        return render(request, 'song_id_edit.html', context)

    elif request.method == 'POST':
        if request.POST['button'] == 'Update':

            errors = Song.objects.validate_song(request.POST)

            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect(f'/song/{song_id}/edit')
            else:
                song.title = request.POST['title']
                song.artist = request.POST['artist'].strip()
                song.save()

        elif request.POST['button'] == 'Delete':
            song.delete()

    return redirect('/')

def song_id_like(request, song_id):

    user = User.objects.get(id = request.session['user_id'])
    song = Song.objects.get(id=song_id)

    if song in user.liked_songs.all():
        user.liked_songs.remove(song.id)

    else:
        user.liked_songs.add(song.id)

    return redirect(request.GET['redirect_uri'])

def playlist_id_song_id_toggle(request, playlist_id, song_id):

    playlist = Playlist.objects.get(id=playlist_id)
    song = Song.objects.get(id=song_id)

    if song in playlist.songs.all():
        playlist.songs.remove(song.id)
        return redirect(f'/playlist/{playlist_id}')
    else:
        playlist.songs.add(song.id)
        return redirect(f'/')

def playlist_new(request):

    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        return render(request, 'playlist_new.html')

    elif request.method == 'POST':

        errors = Playlist.objects.validate_playlist(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/playlist/new')
        else:
            playlist = Playlist.objects.create(name=request.POST['playlist_name'], desc=request.POST['playlist_desc'], user=user)

    return redirect('/')

def playlist_id_edit(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        context={
            'all_playlists': Playlist.objects.all(), # all playlists for user
            'playlist': playlist, # specific playlist
            'playlist_songs': playlist.songs.all(),
            'all_songs': Song.objects.all(),
            'user': user
        }
        return render(request, 'playlist_id_edit.html', context)

    elif request.method == 'POST':
        if request.POST['button'] == 'Update':

            errors = Playlist.objects.validate_playlist(request.POST)

            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect(f'/playlist/{playlist_id}/edit')
            else:
                playlist.name = request.POST['playlist_name']
                playlist.desc = request.POST['playlist_desc'].strip()
                playlist.save()

                return redirect('/')

        elif request.POST['button'] == 'Delete':
            playlist.delete()
            return redirect('/')

    return redirect(f'/playlist/{playlist_id}')

def playlist_id(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    user = User.objects.get(id=request.session['user_id'])

    context={
        'playlist': playlist,
        'user': user,
        'playlist_songs': playlist.songs.all(),
        'liked_songs': user.liked_songs.all()
    }
    return render(request, 'playlist_id.html', context)


# To get all songs for a playlist
#   playlist = Playlist.objects.get(id=playlist_id)
#   all_songs_in_playlist = playlistName.songs.all()
#       for songs in all_songs_in_playlist:
#           songs.title