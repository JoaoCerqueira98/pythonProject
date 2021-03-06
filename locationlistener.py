"""Receives tweets matching a search string and stores a list of dictionaries containing each tweet's screen_name
/text/location"""
import tweepy
from tweetutilities import get_tweet_content


class LocationListener(tweepy.StreamListener):
    """Handles incoming Tweet Stream to get location data."""

    def __init__(self, api, counts_dict, tweets_list, topic, limit=10):
        """Configure the LocationListener."""
        self.tweets_list = tweets_list
        self.counts_dict = counts_dict
        self.topic = topic
        self.TWEET_LIMIT = limit
        super().__init__(api)  # call superclass init

    def on_status(self, status):
        """Called when Twitter pushes a new tweet to you."""
        # get each tweet's screen_name, text and location
        tweet_data = get_tweet_content(status, location=True)

        # ignore retweets and tweet that do not contain the topic
        if tweet_data['text'].startswith('RT') or self.topic.lower() not in tweet_data['text'].lower():
            return

        self.counts_dict['total_tweets'] += 1

        # ignore tweets with no location
        if not status.user.location:
            return

        self.counts_dict['locations'] += 1
        self.tweets_list.append(tweet_data)
        print(f'{status.user.screen_name}: {tweet_data["text"]}\n')

        # If TWEET_LIMIT is reached, return False to terminate streaming
        return self.counts_dict['locations'] < self.TWEET_LIMIT
