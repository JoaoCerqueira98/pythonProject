import tweepy
import keys
from tweetlistener import TweetListener
import geopy
import folium
import pandas as pd
from tweetutilities import get_API, get_geocodes
from locationlistener import LocationListener

api = get_API()
tweets = []
counts = {'total_tweets': 0, 'locations': 0}
location_listener = LocationListener(api, counts_dict=counts, tweets_list=tweets, topic='Football', limit=50)
stream= tweepy.Stream(auth=api.auth, listener=location_listener)
stream.filter(track=['Football'], languages=['en'], is_async=False)
print(f'{counts["locations"] / counts["total_tweets"]:.1%}')
bad_locations = get_geocodes(tweets)
df = pd.DataFrame(tweets)
df = df.dropna()
usmap = folium.Map(location=[39.8283, -98.5795], tiles='Stamen Terrain', zoom_start=4, detect_retina=True)
for t in df.itertuples():
    text = ': '.join([t.screen_name, t.text])
    popup = folium.Popup(text, parse_html=True)
    marker = folium.Marker((t.latitude, t.longitude), popup=popup)
    marker.add_to(usmap)

usmap.save('tweet_map.html')