from django.db import models
import re
import bcrypt
from datetime import date

class UserManager(models.Manager):
    def validate_registration(self, postData):
        errors = {}

        if len(postData['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters."

        if len(postData['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters."

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):    # test whether a field matches the pattern
            errors['email'] = "Invalid email address!"

        # if same email is found in db, show error
        user = User.objects.filter(email=postData['email'])
        if len(user) > 0:
            print("Email already exists!")
            errors['email'] = "Email already exists."

        # check if user is older than 13
        birthday = postData['birthday']
        birthday_result = check_birthday(birthday)
        if birthday_result!= True:
            errors['birthday'] = "You must be at least 13 years old to register."

        if postData['password'] != postData['confirm_password']:
            errors['password'] = "Passwords don't match!"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."

        return errors


    def validate_login(self, postData):
        errors = {}

        user = User.objects.filter(email=postData['login_email'])

        if len(User.objects.filter(email=postData['login_email'])) == 0:
            print("User was not found!")
            errors['login_email'] = "Email was not found, please register."
        else:
            if not bcrypt.checkpw(postData['login_password'].encode(), user[0].password.encode()):
                print("Passwords DON'T match!")
                errors['login_password'] = "Password was incorrect!"

        return errors

def check_birthday(birthday):
    today = str(date.today()) # IMPORT DATE
    today_year_str = ""
    birthday_year_str = ""

    for i in range( len(birthday) - 6 ):
        birthday_year_str += birthday[i]

    for i in range( len(today) - 6 ):
        today_year_str += today[i]

    if ( int(today_year_str) - int(birthday_year_str) ) > 13:
        return True


class PlaylistManager(models.Manager):
    def validate_playlist(self, postData):
        errors = {}

        name = postData['playlist_name'].strip()
        desc = postData['playlist_desc'].strip()

        if len(name) == 0:
            errors['name'] = "Playlist name is required."
        elif len(name) < 3:
            errors['name'] = "Playlist name must be at least 3 characters."

        if len(desc) == 0:
            errors['desc'] = "Playlist description is required."
        elif len(desc) < 3:
            errors['desc'] = "Playlist description must be at least 3 characters."

        # see if playlist name already exists
        # Note: description will be optional
        playlistNameList = Playlist.objects.filter(name=name)

        if len(playlistNameList) > 0:
            errors['name'] = "This playlist name already exists!"

        return errors


class SongManager(models.Manager):
    def validate_song(self, postData):
        errors = {}

        title = postData['title'].strip()
        artist = postData['artist'].strip()
        songTitleList = Song.objects.filter(title=title).filter(artist=artist)

        if len(songTitleList) > 0:
            errors['general'] = "This song for this artist already exists!"
        if len(title) == 0:
            errors['title'] = "Song title is required."
        elif len(title) < 3:
            errors['title'] = "Song title must be at least 3 characters."

        if len(artist) == 0:
            errors['artist'] = "Song artist is required."
        elif len(artist) < 3:
            errors['artist'] = "Song artist must be at least 3 characters."

        return errors

# ---------- CLASSES --------- #

class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    birthday = models.DateField()
    password = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # playlists = LIST of playlists created by a user
    # liked_songs = LIST of songs a user likes

    objects = UserManager()


class Song(models.Model):
    title = models.CharField(max_length=50)
    artist = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users_who_like = models.ManyToManyField(User, related_name="liked_songs")
    # a LIST of users who like a song
    # playlists = LIST of playlists that song have been added to
    image_url = models.CharField(max_length=200)

    objects = SongManager()


class Playlist(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name="playlists", on_delete = models.CASCADE)
    # the user who created the playlist
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    songs = models.ManyToManyField(Song, related_name="playlists")
    # LIST of songs within playlist

    objects = PlaylistManager()



