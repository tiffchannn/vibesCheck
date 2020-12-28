from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import bcrypt
from datetime import date

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
import pprint


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        errors = User.objects.validate_registration(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        form_password = request.POST['password']
        pw_hash = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt()).decode()

        created_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            birthday = request.POST['birthday'],
            password = pw_hash
            )

        request.session['user_id'] = created_user.id

        messages.success(request, "Registration was successful, please login!")

        print('New User: ', created_user)
        return redirect('/')

def login(request):
    if request.method == 'POST':
        errors = User.objects.validate_login(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            user = User.objects.get(email=request.POST['login_email'])
            request.session['user_id'] = user.id

            print('User ID:', user.id)
            return redirect('/dashboard')

def dashboard(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please log in!")
        return redirect('/')

    user = User.objects.get(id=request.session['user_id'])
    liked_songs = user.liked_songs.all()

    context = {
        "user": User.objects.get(id=user.id),
        "all_playlists": Playlist.objects.all(),
        "all_songs": Song.objects.all(),
        "liked_songs": liked_songs# user's liked songs
    }
    return render(request, 'dashboard.html', context)


def create_song(request):
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        return render(request, 'create_song.html')

    elif request.method == 'POST':
        if request.POST['button'] == "Create New Song":
            print('this is creating a new song')

        errors = Song.objects.validate_song(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/vibesCheck/newSong')
        else:
            form_title = request.POST['title']
            form_artist = request.POST['artist']
            song = Song.objects.create(title=form_title, artist=form_artist)
            print("Song ID: " + str(song.id))

            print('-'*70)
            print('New Song Added: ', request.POST)
            return redirect('/dashboard')

def search_song(request):
    if request.method == 'POST':
        search_str = request.POST['title']

        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id="cf3e3d623cae428987e52a41c5f9ad8a",client_secret="522fb8f9cc734d4f9b3c62c39cd19c1f"))
        results = sp.search(search_str, limit = 5)

        user = User.objects.get(id=request.session['user_id'])
        liked_songs = user.liked_songs.all()

        # return JsonResponse(results)


        search_results = []
        for song in results['tracks']['items']:
            song_info = {
                "name": "",
                "artist": "",
                "image_url": ""
            }
            song_info['name'] = song['name']
            song_info['image_url'] = song['album']['images'][1]['url']
            print('Image Url: ', song_info['image_url'], 'Height: ', song['album']['images'][1]['height'])


            song_artists_list = []
            for artist in song['artists']:
                song_artists_list.append(artist['name'])
            song_info['artist'] = ", ".join(song_artists_list)
            search_results.append(song_info)

        songs = []
        for result in search_results:
            search_song = {
                'title': result['name'],
                'artist': result['artist'],
                'image_url': result['image_url']
            }
            print('Song Title: ', result['name'])

            print('Artist: ', result['artist'])


            # take search results and add info into db as new song
            errors = Song.objects.validate_song(search_song)
            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                # return redirect('/vibesCheck/newSong')
            else:
                song = Song.objects.create(title=search_song['title'], artist=search_song['artist'], image_url=search_song['image_url'])
                songs.append(song)
                print("Song ID: " + str(song.id))

                print('-'*70)
                print('New Song Added: ', song)


        context = {
            "user": User.objects.get(id=user.id),
            "all_playlists": Playlist.objects.all(),
            "all_songs": Song.objects.all(),
            "liked_songs": liked_songs, # user's liked songs
            "songs": songs # list of songs that were added from the search bar
        }

        return render(request, 'create_song.html', context)


def song_info(request, song_id):

    song = Song.objects.get(id=song_id)
    user = User.objects.get(id=request.session['user_id'])

    context = {
        'song': song,
        'user': user,
        'liked_songs': user.liked_songs.all()
    }
    return render(request, 'song_info.html', context)


def edit_song(request, song_id):

    song = Song.objects.get(id=song_id)
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        context={
            'song': song,
            'user': user
        }
        return render(request, 'edit_song.html', context)

    elif request.method == 'POST':
        if request.POST['button'] == 'Update':
            print('this is updating id: ' + str(song_id))

            errors = Song.objects.validate_song(request.POST)
            user = User.objects.get(id=request.session['user_id'])

            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect(f'/vibesCheck/editSong/{song_id}')
            else:
                song_to_update = Song.objects.get(id=song_id)
                song_to_update.title = request.POST['title']
                song_to_update.artist = request.POST['artist'].strip()
                song_to_update.save()

                print('Song was updated!', request.POST)
                return redirect('/dashboard')

        elif request.POST['button'] == 'Delete':
            song_to_delete = Song.objects.get(id=song_id)
            song_to_delete.delete()

            print("Song was deleted!")
            return redirect('/dashboard')

def like_song(request, song_id):

    user = User.objects.get(id = request.session['user_id'])
    song = Song.objects.get(id=song_id)

    if song not in user.liked_songs.all():
        user.liked_songs.add(song.id)
        print('-'*70)
        print('Song was liked!', str(song.title))
    else:
        user.liked_songs.remove(song.id)
        print('-'*70)
        print('Song was unliked!', str(song.title))

    return redirect(request.GET['redirect_uri'])

def add_song_to_playlist(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    song = Song.objects.get(id=request.GET['song_id'])

    if song not in playlist.songs.all():
        playlist.songs.add(song.id)
        print('-'*70)
        print('Song was added to playlist!', str(song.title), '\nPlaylist :', playlist.name)

    return redirect('/dashboard')

def create_playlist(request):

    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        return render(request, 'create_playlist.html')

    elif request.method == 'POST':
        if request.POST['button'] == "Create A Vibe":
            print('This is creating a playlist')

        errors = Playlist.objects.validate_playlist(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/vibesCheck/newPlaylist')
        else:
            form_playlist_name = request.POST['playlist_name']
            form_desc = request.POST['playlist_desc']
            playlist = Playlist.objects.create(name=form_playlist_name, desc=form_desc, user=user)
            print("Playlist ID: " + str(playlist.id))

            print('-'*70)
            print('New Playlist Added: ', request.POST)
            return redirect('/dashboard')

def edit_playlist(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'GET':
        context={
            "all_playlists": Playlist.objects.all(), # all playlists for user
            'playlist': playlist, # specific playlist
            'playlist_songs': playlist.songs.all(),
            "all_songs": Song.objects.all(),
            'user': user
        }
        return render(request, 'edit_playlist.html', context)

    elif request.method == 'POST':
        if request.POST['button'] == 'Update':

            errors = Playlist.objects.validate_playlist(request.POST)
            user = User.objects.get(id=request.session['user_id'])

            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect(f'/vibesCheck/editPlaylist/{playlist_id}')
            else:
                playlist_to_update = Playlist.objects.get(id=playlist_id)
                playlist_to_update.name = request.POST['playlist_name']
                playlist_to_update.desc = request.POST['playlist_desc'].strip()
                playlist_to_update.save()

                print('Playlist was updated!', request.POST)
                return redirect('/dashboard')

        elif request.POST['button'] == 'Delete':
            playlist_to_delete = Playlist.objects.get(id=playlist_id)
            playlist_to_delete.delete()

            print("Playlist was deleted!")
            return redirect('/dashboard')



def playlist_info(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    user = User.objects.get(id=request.session['user_id'])

    context={
        'playlist': Playlist.objects.get(id=playlist_id),
        'user': User.objects.get(id=request.session['user_id']),
        'playlist_songs': playlist.songs.all(),
        'liked_songs': user.liked_songs.all()
    }
    return render(request, 'playlist_info.html', context)

def remove_song_from_playlist(request, playlist_id):

    playlist = Playlist.objects.get(id=playlist_id)
    song_id = request.GET['song_id']
    playlist.songs.remove(song_id)

    print('Song was removed from playlist!', song_id)
    return redirect(f'/vibesCheck/playlist/{playlist_id}')


def logout(request):

    request.session.clear()

    print("Logged Out!")
    messages.success(request, "You have been logged out!")
    return redirect('/')


# To get all songs for a playlist
#   playlist = Playlist.objects.get(id=playlist_id)
#   all_songs_in_playlist = playlistName.songs.all()
#       for songs in all_songs_in_playlist:
#           songs.title