import sql_server as ss
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import warnings
from config import *

warnings.simplefilter('ignore')
artists = ss.query_sql("select a.artist_id,a.name,a.popularity from tracks t inner join track_artists ta on t.track_id=ta.track_id " \
                       "inner join albums al on t.album_id=al.album_id " \
                       "inner join album_artists aa on al.album_id=aa.album_id inner join artists a on aa.artist_id=a.artist_id " \
                       "where ta.artist_id = '3TVXtAsR1Inumwj472S9r4' and " \
                       "aa.artist_id not in ('3TVXtAsR1Inumwj472S9r4','0LyfQWJT6nXafLPZqxe9Of') group by a.name order by a.name")
x = []
y = []
c = []
label = []

for artist in artists:
     artist_songs = ss.query_sql('select d.popularity from tracks t ' \
                                 'inner join drake_songs d on t.track_id=d.track_id ' \
                                 'inner join albums al on t.album_id=al.album_id ' \
                                 'inner join album_artists aa on al.album_id=aa.album_id ' \
                                 'where t.track_id not in (select * from drake_tracks) and aa.artist_id="'+artist[0]+'" ' \
                                 'group by t.track_id')
     artist_songs = [int(row[0]) for row in artist_songs]

     drake_features = ss.query_sql('select d.popularity from tracks t ' \
                                   'inner join drake_songs d on t.track_id=d.track_id ' \
                                   'inner join albums al on t.album_id=al.album_id ' \
                                   'inner join album_artists aa on al.album_id=aa.album_id ' \
                                   'inner join drake_tracks dt on t.track_id=dt.track_id ' \
                                   'where aa.artist_id="'+artist[0]+'" ' \
                                   'group by t.track_id')
     count = ss.query_sql('select count(distinct t.track_id) from tracks t ' \
                          'inner join drake_songs d on t.track_id=d.track_id ' \
                          'inner join albums al on t.album_id=al.album_id ' \
                          'inner join album_artists aa on al.album_id=aa.album_id ' \
                          'inner join drake_tracks dt on t.track_id=dt.track_id ' \
                          'where aa.artist_id="'+artist[0]+'"')[0][0]
     drake_features = [int(row[0]) for row in drake_features]
     non_drake_mean = round(np.mean(artist_songs),1)
     non_drake_median = np.median(artist_songs)
     drake_mean = round(np.mean(drake_features),1)
     drake_median = np.median(drake_features)
     mean_diff = drake_mean - non_drake_mean
     median_diff = drake_median - non_drake_median
     x.append(non_drake_median)
     y.append(median_diff)
     c.append(count)
     label.append(artist[1])
     #print non_drake_median,median_diff,count,artist[1]

fig,ax = plt.subplots()
plot = plt.scatter(x, y, c=c, cmap=cm.jet)
ax.set_xlabel("Artist's Median Song Popularity")
ax.set_ylabel("Median Song Popularity Difference with/without Drake")
ax.set_title("Effect of Drake Feature on Artists' Spotify Song Popularity")
colorbar = fig.colorbar(plot,label='Number of tracks featuring Drake',ticks=[1,5,10,15],boundaries=range(16))
colorbar.ax.set_yticklabels(['1','5','10','15'])
plt.axhline(y=0,c='black')
for i in range(len(label)):
     if label[i] == 'Future':
          ax.annotate(label[i], xy=(x[i],y[i]), xycoords='data', xytext=(5,-20),
                      textcoords='offset points', arrowprops=dict(arrowstyle='-'))
     elif label[i] == 'Rihanna':
          ax.annotate(label[i], xy=(x[i],y[i]), xycoords='data', xytext=(-5,-15),
                      textcoords='offset points', arrowprops=dict(arrowstyle='-'))
     elif label[i] == 'Chris Brown':
          ax.annotate(label[i], xy=(x[i],y[i]), xycoords='data', xytext=(-35,20),
                      textcoords='offset points', arrowprops=dict(arrowstyle='-'))
     elif label[i] == 'N.E.R.D':
          ax.annotate(label[i], xy=(x[i],y[i]), xycoords='data', xytext=(-10,-20),
                      textcoords='offset points', arrowprops=dict(arrowstyle='-'))

plt.show()
