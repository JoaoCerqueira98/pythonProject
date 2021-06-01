from geopy import OpenMapQuest
import keys
from textblob import TextBlob
import time
import tweepy


def get_API(wait=True, notify=True):
    """ Authenticate with Twitter and return API object"""
    # configure the OAuthHandler
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)

    # get the API object
    return tweepy.API(auth, wait_on_rate_limit=wait, wait_on_rate_limit_notify=notify)


def print_tweets(tweets):
    """For each Tweepy Status object in tweets, display the user's screen_name and tweet text. If the language is not
    English, translate the text with TextBlob """
    for tweet in tweets:
        print(f'{tweet.user.screen_name}: ', end=' ')

        if 'en' in tweet.lang:
            print(f'{tweet.text}\n')
        elif 'und' not in tweet.lang:
            print(f'\n Original: {tweet.text}')
            print(f'\n Translated: {TextBlob(tweet.text).translate()}\n')


def get_tweet_content(tweet, location=False):
    fields = {'screen_name': tweet.user.screen_name}

    # get the tweet's text
    try:
        fields['text'] = tweet.extended_tweet.full_text
    except:
        fields['text'] = tweet.text

    if location:
        fields['location'] = tweet.user.location

    return fields


def get_geocodes(tweet_list):
    """Get the latitude and longitude for each tweet's location.
    Returns the number of tweets with invalid location data"""
    print('Getting coordinates for tweet locations...')
    geo = OpenMapQuest(api_key=keys.mapquest_key)
    bad_locations = 0

    for tweet in tweet_list:
        processed = False
        delay = .1
        while not processed:
            try:
                geo_location = geo.geocode(tweet['location'])
                processed = True
            except:
                print('OpenMapQuest service timed out. Waiting')
                time.sleep(delay)
                delay += .1
        if geo_location:
            tweet['latitude'] = geo_location.latitude
            tweet['longitude'] = geo_location.longitude
        else:
            bad_locations += 1
    print('Done geocoding')
    return bad_locations
