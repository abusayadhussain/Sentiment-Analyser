from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob

import twitter_credentials
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt


# Twitter client

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAunthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_api_client(self):
        return self.twitter_client    

    def get_user_timeline_tweets(self, num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets 
    def get_friend_list(self, num_friend):
        friend_list=[]
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friend):
            friend_list.append(friend)
        return friend_list   
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets    


# Twitter authenticator
class TwitterAunthenticator:
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer:
    #This class is responsible for streaming and processing live tweets
    def __init__(self):
        self.twitter_authenticator = TwitterAunthenticator()

    def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
        # twitter authetication and the connection to twitter streaming api
        Listener = TwitterListener(fetched_tweet_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, Listener)
        stream.filter(track=hash_tag_list) 



class TwitterListener(StreamListener):
    #This class is responsible for prints recieved live tweets 

    def __init__(self, fetched_tweet_filename):
        self.fetched_tweet_filename = fetched_tweet_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweet_filename, 'a') as tf:
                tf.write(data)
            return True    
        except BaseException as e:
            print("Error on data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            return False
        print(status)

class TweetAnalyzer():
    #analyzing content from tweets

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analyze = TextBlob(self.clean_tweet(tweet))

        if analyze.sentiment.polarity > 0:
            return 'Positive'
        elif analyze.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'    

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df

if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_api_client()

    tweets = api.user_timeline(screen_name='dota2', count=20)
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    print(df.head(10))
    # Get average length of the tweets
    print(np.mean(df['len']))   

    # get the maximum likes a tweet get
    print(np.max(df['likes']))  

     # get the maximum retweeted tweet get
    print(np.max(df['retweets'])) 

    #Time Series

    time_likes = pd.Series(df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), label='likes', legend=True)

    time_retwees = pd.Series(df['retweets'].values, index=df['date'])
    time_retwees.plot(figsize=(16,4), label='retweets', legend=True)

    plt.show()