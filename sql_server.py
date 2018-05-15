import pymysql
from config import *

def sql_connect():
    connection = pymysql.connect(host=sqlVals['host'],
                                 port=sqlVals['port'],
                                 user=sqlVals['user'],
                                 password=sqlVals['password'],
                                 db=sqlVals['db'])
    return connection

def sql_end(connection):
    connection.commit()
    connection.close()

def create_db():
     connection = sql_connect()
     cursor = connection.cursor()

     artist_sql = "create table Artists (" \
                "artist_id varchar(30) NOT NULL," \
                "name varchar(255)," \
                "popularity tinyint unsigned," \
                "PRIMARY KEY (artist_id))"

     cursor.execute(artist_sql)

     album_sql = "create table Albums (" \
                "album_id varchar(30) NOT NULL," \
                "name varchar(255)," \
                "popularity tinyint unsigned," \
                "release_date date," \
                "album_type varchar(255)," \
                "PRIMARY KEY (album_id))"

     cursor.execute(album_sql)

     track_sql = "create table Tracks (" \
                "track_id varchar(30) NOT NULL," \
                "name varchar(255)," \
                "popularity tinyint unsigned," \
                "album_id varchar(30)," \
                "track_number smallint," \
                "acousticness float," \
                "danceability float," \
                "duration_ms int," \
                "energy float," \
                "instrumentalness float," \
                "music_key int," \
                "liveness float," \
                "loudness float," \
                "mode tinyint unsigned," \
                "speechiness float," \
                "tempo float," \
                "time_signature tinyint unsigned," \
                "valence float," \
                "is_explicit tinyint unsigned," \
                "PRIMARY KEY (track_id)," \
                "FOREIGN KEY (album_id) REFERENCES Albums (album_id))"

     cursor.execute(track_sql)

     artist_genres_sql = "create table artist_genres (" \
                       "artist_id varchar(30) NOT NULL," \
                       "genre varchar(255) NOT NULL," \
                       "PRIMARY KEY (artist_id, genre)," \
                       "FOREIGN KEY (artist_id) REFERENCES Artists (artist_id))"

     cursor.execute(artist_genres_sql)

     track_artists_sql = "create table track_artists (" \
                       "track_id varchar(30)," \
                       "artist_id varchar(30)," \
                       "PRIMARY KEY (track_id, artist_id)," \
                       "FOREIGN KEY (track_id) REFERENCES Tracks (track_id)," \
                       "FOREIGN KEY (artist_id) REFERENCES Artists (artist_id))"

     cursor.execute(track_artists_sql)

     album_artists_sql = "create table album_artists (" \
                       "album_id varchar(30)," \
                       "artist_id varchar(30)," \
                       "PRIMARY KEY (album_id, artist_id)," \
                       "FOREIGN KEY (album_id) REFERENCES Albums (album_id)," \
                       "FOREIGN KEY (artist_id) REFERENCES Artists (artist_id))"

     cursor.execute(album_artists_sql)
     
     connection.close()

     print "Tables created."

def insert_sql(insert):
    connection = sql_connect()
    cursor = connection.cursor()
    try:
        cursor.execute(insert)
    except Exception as e:
        print "ERROR: ",e
        print "Failed query: ",insert
    sql_end(connection)

def insert_multi_sql(inserts):
    connection = sql_connect()
    cursor = connection.cursor()
    for insert in inserts:
        try:
            cursor.execute(insert)
        except Exception as e:
            print "ERROR: ",e
            print "Failed query: ",insert
    sql_end(connection)

def query_sql(query):
    connection = sql_connect()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    sql_end(connection)
    return results

if __name__ == "__main__":
     create_db()
