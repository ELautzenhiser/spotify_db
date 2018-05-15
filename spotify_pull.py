import spotipy,unicodedata,re,warnings,time
from sql_server import *
from config import *
from spotipy import oauth2

def clean_string(string):
     return re.sub(r"\\",r"\\\\",
                    re.sub("'","''",
                    unicodedata.normalize('NFKD',string).encode('ascii','ignore')))

def create_artist_sql(artists_dict):
     artists_sql = 'insert ignore into artists (artist_id, name, popularity) values'
     for artist in artists_dict:
          artist_data = artists_dict[artist]
          artists_sql += "('{0}','{1}',{2}),".format(artist,artist_data['name'],
                                                 artist_data['popularity'])
     artists_sql = artists_sql[:-1]
     return artists_sql

def create_art_genre_sql(artists_dict):
     genre_sql = 'insert ignore into artist_genres (artist_id, genre) values '
     for artist in artists_dict:
          genres = artists_dict[artist]['genres']
          for genre in genres:
               genre_sql += "('{0}','{1}'),".format(artist,genre)
     genre_sql = genre_sql[:-1]
     return genre_sql

def put_album_sql(album_dict):
     album_id = album_dict['album_id']
     artist_sql = 'insert ignore into artists (artist_id) values '
     alb_art_sql = 'insert ignore into album_artists (album_id, artist_id) values '
     
     for artist_id in album_dict['album_artists']:
          artist_sql += "('{0}'),".format(artist_id)
          alb_art_sql += "('{0}','{1}'),".format(album_id, artist_id)

     album_sql = "insert ignore into albums (album_id, name, popularity, " \
                 "release_date, album_type) values ('{0}','{1}',{2},'{3}', " \
                 "'{4}')".format(album_id,
                                 album_dict['name'],
                                 album_dict['popularity'],
                                 album_dict['release_date'],
                                 album_dict['album_type'])

     artist_sql = artist_sql[:-1]
     alb_art_sql = alb_art_sql[:-1]

     insert_multi_sql([artist_sql, album_sql, alb_art_sql])

def put_track_sql(tracks_dict):
     artist_sql = 'insert ignore into artists (artist_id) values '
     track_sql = 'insert ignore into tracks (track_id, name, popularity, ' \
                 'album_id, track_number, acousticness, danceability, ' \
                 'duration_ms, energy, instrumentalness, music_key, liveness, ' \
                 'loudness, mode, speechiness, tempo, time_signature, valence, ' \
                 'is_explicit) values '
     track_art_sql = 'insert ignore into track_artists (track_id, artist_id) ' \
                     'values '

     artist_list = []
     
     for track in tracks_dict:
          t_data = tracks_dict[track]
          for key in t_data:
               if t_data[key] is None:
                    t_data[key] = 'Null'
          track_sql += "('{0}','{1}',{2},'{3}',{4},{5},{6},{7},{8},{9},{10}," \
                       "{11},{12},{13},{14},{15},{16},{17},{18}),".format(
                            track, t_data.get('name'), t_data.get('popularity'),
                            t_data.get('album_id'), t_data.get('track_number'),
                            t_data.get('acousticness'), t_data.get('danceability'),
                            t_data.get('duration_ms'), t_data.get('energy'),
                            t_data.get('instrumentalness'), t_data.get('key'),
                            t_data.get('liveness'), t_data.get('loudness'), t_data.get('mode'),
                            t_data.get('speechiness'), t_data.get('tempo'),
                            t_data.get('time_signature'), t_data.get('valence'),
                            t_data.get('explicit'))

          for artist in t_data['artists']:
               track_art_sql += "('{0}','{1}'),".format(track,artist)
               if artist not in artist_list:
                    artist_list.append(artist)
                    
     for artist in artist_list:
          artist_sql += "('{0}'),".format(artist)

     artist_sql = artist_sql[:-1]
     track_sql = track_sql[:-1]
     track_art_sql = track_art_sql[:-1]

     insert_sql(artist_sql)
     insert_sql(track_sql)
     insert_sql(track_art_sql)
                            
def get_artist_from_name(spotify, name, artists_dict):
     raw_results = spotify.search(q='artist:'+name, type='artist')
     results = raw_results['artists']['items']
     if results:
          artist_info = results[0]
          return get_artist(artist_info, artists_dict)
     else:
          return artists_dict

def get_artist_from_id(spotify, artist_id, artists_dict):
     artist_info = spotify.artist(artist_id)
     return get_artist(artist_info, artists_dict)

def get_artist(artist_info, artists_dict):
     artist_id = clean_string(artist_info['id'])
     artist_name = clean_string(artist_info['name'])
     artist_popularity = artist_info['popularity']
     artist_genres = [clean_string(genre) for genre in artist_info['genres']]
     artist_dict = {'name' : artist_name, 'popularity' : artist_popularity,
                    'genres' : artist_genres}
     artists_dict[artist_id] = artist_dict

     return artists_dict
     
def get_album(spotify, album_id, albums_dict):
     if query_sql('select count(*) from albums where album_id='+album_id) != 0:
          return
     time.sleep(2)
     album_info = spotify.album(album_id)
     album_name = clean_string(album_info['name'])
     album_type = clean_string(album_info['album_type'])
     album_date = album_info['release_date']
     if album_info['release_date_precision'] == 'year':
          album_date = album_date+'-01-01'
     album_popularity = album_info['popularity']
     album_artists = [clean_string(artist['id']) for artist in album_info['artists']]
     album_dict = {'album_id' : album_id, 'name' : album_name, 'album_type' : album_type,
                   'release_date' : album_date, 'popularity' : album_popularity,
                   'album_artists' : album_artists}
     albums_dict[album_id] = album_dict
     put_album_sql(album_dict)
     get_album_tracks(spotify, album_id)

def get_track_popularity(spotify, track_id):
     track_info = spotify.track(track_id)
     return track_info['popularity']

def get_track_features(spotify, track_id):
     features = spotify.audio_features(track_id)[0]
     if not features:
          return dict()
     track_dict = {'energy' : features.get('energy'), 'liveness' : features.get('liveness'),
                   'tempo' : features.get('tempo'), 'speechiness' : features.get('speechiness'),
                   'acousticness' : features.get('acousticness'),
                   'instrumentalness' : features.get('instrumentalness'),
                   'time_signature' : features.get('time_signature'),
                   'danceability' : features.get('danceability'),
                   'key' : features.get('key'), 'loudness' : features.get('loudness'),
                   'valence' : features.get('valence'), 'mode' : features.get('mode'),
                   'duration_ms' : features.get('duration_ms')}

     return track_dict
     
def get_album_tracks(spotify, album_id):
     tracks_dict = {}
     album_tracks = spotify.album_tracks(album_id)
     while True:
          tracks_list = album_tracks['items']
          for track in tracks_list:
               track_id = clean_string(track['id'])
               track_dict = get_track_features(spotify, track_id)
               track_dict['artists'] = [clean_string(artist['id']) for artist in track['artists']]
               track_dict['name'] = clean_string(track['name'])
               track_dict['album_id'] = album_id
               track_dict['track_number'] = track['track_number']
               track_dict['popularity'] = get_track_popularity(spotify, track_id)
               track_dict['album'] = album_id
               if track['explicit'] == True:
                    track_dict['explicit'] = 1
               else:
                    track_dict['explicit'] = 0
               tracks_dict[track_id] = track_dict
          if not album_tracks.get('next'):
               put_track_sql(tracks_dict)
               return tracks_dict
          else:
               album_tracks = spotify.next(album_tracks)
               

def get_artist_albums(spotify, artist_id):
     albums_dict = {}
     try:
          raw_results = spotify.artist_albums(artist_id, limit=20, country="US")
     except:
          print "ERROR: Couldn't get albums for artist "+str(artist_id)
          return albums_dict
     while True:
          album_list = raw_results['items']
          for album in album_list:
               album_id = clean_string(album['id'])
               albums_dict = get_album(spotify, album_id, albums_dict)
          if not raw_results.get('next'):
               return albums_dict
          else:
               raw_results = spotify.next(raw_results)
     
def update_artists(spotify):
     print "Updating artists"
     artists_list = query_sql('select artist_id from artists where name is null')
     artists_dict = dict()
     count = 0
     for artist in artists_list:
          artist_id = artist[0]
          artists_dict = get_artist_from_id(spotify, artist_id, artists_dict)
          count += 1
          if count%10 == 0:
               time.sleep(2)
               print '.',

     update_statements = []
     genres_sql = 'insert into artist_genres (artist_id, genre) values '
     for artist_id in artists_dict:
          artist_info = artists_dict[artist_id]
          sql = "update artists set name = '{0}', popularity = {1} where artist_id = '{2}'".format(artist_info['name'],
                                                                                                   artist_info['popularity'],
                                                                                                   artist_id)
          update_statements.append(sql)
          
          for genre in artist_info['genres']:
               genres_sql += "('{0}','{1}'),".format(artist_id,genre)

     genres_sql = genres_sql[:-1]
     update_statements.append(genres_sql)

     insert_multi_sql(update_statements)

     print "Done updating artists"

def clean_database(spotify):
     update_artists(spotify)

def main():
     total_start = time.time()
     warnings.simplefilter('ignore')
     ccm = oauth2.SpotifyClientCredentials(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET)

     spotify = spotipy.Spotify(client_credentials_manager=ccm)

     artists_dict = dict()
     artist_names = ['Taylor Swift','Rihanna', 'Selena Gomez',
                     'Ed Sheeran', 'The Weeknd', 'Drake',
                     'Coldplay', 'Maroon 5', 'Imagine Dragons']

     for name in artist_names:
          artists_dict = get_artist_from_name(spotify, name, artists_dict)
     
     artists_sql = create_artist_sql(artists_dict)
     insert_sql(artists_sql)

     genre_sql = create_art_genre_sql(artists_dict)
     insert_sql(genre_sql)

     for artist_id in artists_dict:
          print "Getting albums for artist: "+artists_dict[artist_id]['name']
          get_artist_albums(spotify, artist_id)

     clean_database(spotify)
     total_end = time.time()
     print "Total time elapsed: "+str(total_end - total_start)

     
if __name__ == '__main__':
     main()
