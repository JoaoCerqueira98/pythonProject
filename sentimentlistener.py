import keys
import preprocessor as p
import sys
import tweepy
from textblob import TextBlob


class SentimentListener(tweepy.StreamListener):
    """Handles incoming Tweet stream."""

    def __init__(self, api, sentiment_dict, topic, limit=10):
        """Configure the sentiment listener"""
        self.sentiment_dict = sentiment_dict
        self.tweet_count = 0
        self.topic = topic
        self.TWEET_LIMIT = limit

        # set twett-preprocessor to remove URL's/reserved words
        p.set_options(p.OPT.URL, p.OPT.RESERVED)
        super().__init__(api)

    def on_status(self, status):
        """Called when Twitter pushes a new tweet to you"""
        # get the tweet text
        try:
            tweet_text = status.extended_tweet.full_text
        except:
            tweet_text = status.text

        # ignore retweets
        if tweet_text.startswith('RT'):
            return

        tweet_text = p.clean(tweet_text)

        # ignore tweet if the topic is not in the tweet
        if self.topic.lower() not in tweet_text.lower():
            return

            # Update self.sentiment_dict with the polarity
        blob = TextBlob(tweet_text).translate()
        if blob.sentiment.polarity > 0:
            sentiment = '+'
            self.sentiment_dict['positive'] += 1
        elif blob.sentiment.polarity == 0:
            sentiment = ' '
            self.sentiment_dict['neutral'] += 1
        else:
            sentiment = '-'
            self.sentiment_dict['negative'] += 1

        # display the tweet
        print(f'{sentiment} {status.user.screen_name}: {tweet_text}\n')

        self.tweet_count += 1  # track number of tweets processed

        # if TWEET_LIMIT is reached, return False to terminate streaming
        return self.tweet_count <= self.TWEET_LIMIT


def main():
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)

    # get the API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # create the StreamListener subclass object
    search_key = sys.argv[1]
    limit = int(sys.argv[2])
    sentiment_dict = {'positive': 0, 'neutral': 0, 'negative': 0}
    sentiment_listener = SentimentListener(api, sentiment_dict, search_key, limit)

    # set up the stream
    stream = tweepy.Stream(auth=api.auth, listener=sentiment_listener)

    # start filtering English tweets containing search_key
    stream.filter(track=[search_key], languages=['pt'], is_async=False)

    print(f'Tweet sentiment for "{search_key}"')
    print(f'Positive: ', sentiment_dict['positive'])
    print(f'Neutral: ', sentiment_dict['neutral'])
    print(f'Negative: ', sentiment_dict['negative'])


# call main if this file is executed as a script
if __name__ == '__main__':
    main()
