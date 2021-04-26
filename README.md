# Vibes Check
**Music playlist creation and curation CRUD application using Python, Django and Bootstrap**

**Front-End:** Bootstrap, CSS, HTML

**Back-End:** Django

## Join or login to account
Users can create personalized accounts for Vibe Check. 
- Email pattern validations are verified through regex.
- Utilized Bcrypt and hashing to secure and validate passwords.
- Created customized validations into models to ensure data and formatting was accurate prior to persisting data.
- Display errors in real time based on user's input for mismatched password, age restrictions, and duplicate emails.

![alt text](https://media.giphy.com/media/0HbFE2Tg37onBCgmxg/giphy.gif)

## Search and add songs or artists to your account
Manually add or search for songs to add to account. If using search, songs found will be automatically added to the users music collection and can be added to playlists.
- When adding songs manually, backend validations are enforced to determine duplicate entries, song title and artist name length. 
- Song searches are fueled by the **Spotify API**, using their database to browse through artists and songs.
- All songs searched, can be added into pre-existing playlists via dropdown menu or liked by clicking on a heart emoji. 

![alt text](https://media.giphy.com/media/konPkCd5ariB04Otgz/giphy.gif)

## Favorite songs in your account
Users are able to like or un-like a song by clicking on the heart emoji. 

- White hearts :white_heart: are for songs not liked.

- Green hearts :green_heart: are for favorited songs.

![alt text](https://media.giphy.com/media/8SBz2IReqci3rCUDbg/giphy.gif)

## Edit and remove songs or artists 
Update or delete songs from the music collection with a simple button.

![alt text](https://media.giphy.com/media/AESVwvX7zmd0CJjUJP/giphy.gif)

## Add songs to a playlist
Curate a playlist in two ways:
1. Select a specific playlist from the playlist menu bar and add songs manually.
2. Utilize the 'Add to playlit' dropdown menu from a specific song to choose which playlist to customize.

![alt text](https://media.giphy.com/media/75SHCIvs81gjW0Dkae/giphy.gif)

## Create playlist
- New playlists created are validated to ensure there aren't duplicate playlist names or descriptions.
- Validations are set in place when playlists are updated or edited.

![alt text](https://media.giphy.com/media/vMqiCbLkGEcqQEr8of/giphy.gif)

## Challenges and Notes:
- When searching for a song, all songs pulled from the Spotify API are automatically added to a user's account. I would like to potentially prevent this from happening, and allow the user to pick and choose which songs to be saved to their account. I imagine that this could be done within views.py when saving the searches.  
- Hopeful additions and features:
  - Ability to sort the songs that are saved in the database.
  - Song previews and playback options


