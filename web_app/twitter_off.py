from os import getenv
import threading
from queue import Queue, Empty

import basilica
import tweepy  
from dotenv import load_dotenv

from web_app.db.db_model import db, User, Tweet


load_dotenv()

TWITTER_API_KEY = getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_CODE = getenv('TWITTER_ACCESS_CODE')
TWITTER_ACCESS_SECRET_CODE = getenv('TWITTER_ACCESS_SECRET_CODE')
BASILICA_KEY = getenv('BASILICA_KEY')

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, 
                                   TWITTER_API_SECRET_KEY)
TWITTER_AUTH.set_access_token(TWITTER_ACCESS_CODE,
                              TWITTER_ACCESS_SECRET_CODE)
Twitter = tweepy.API(TWITTER_AUTH)

Basilica = basilica.Connection(BASILICA_KEY)

Que = Queue()


def add_twitter_user(username):
    try:
        # Get user information
        twitter_user = Twitter.get_user(username)
    except tweepy.TweepError as err:
        raise Exception(f'{username} not found.')

    # Check if it already exists in the DB
    if User.query.get(twitter_user.id) is not None:
        return True

    # Add user to DB
    db_user = User(id=twitter_user.id, user=username,
                    name=twitter_user.name)
    db.session.add(db_user)

    # Call worker to fetch tweets in background
    th = threading.Thread(target=fetch_tweets, 
                          args=([(twitter_user, db_user, 1)],))
    th.start()
    return False


def updateTweets():
    users = User.query.all()

    twit_users = []
    for user in users:
        last_tweet = user.newest_tweet_id
        try:
            twitter_user = Twitter.get_user(user.user)
        except tweepy.TweepError:
            continue
        twit_users.append((twitter_user, user, last_tweet))

    th = threading.Thread(target=fetch_tweets, args=(twit_users,))
    th.start()
    return
    
    
def fetch_tweets(twitter_users, threshold=200):
    for twitter_user in twitter_users:
        last_tweet = twitter_user[2]
        # Get first batch of tweets
        total_tweets = twitter_user[0].timeline(count=200,
                                        exclude_replies=True,
                                        include_rts=False,
                                        tweet_mode='extended',
                                        since_id=last_tweet)

        # Get oldest and newest tweets
        tweets_found = len(total_tweets)
        print(f'{tweets_found} tweets found for {twitter_user[0].screen_name}.')
        Que.put({'user': twitter_user[0].screen_name, 
                 'count': tweets_found,
                 'status': 0},
                 block=False)
        if tweets_found == 0:
            continue    
        oldest_tweet = total_tweets[-1].id - 1
        twitter_user[1].newest_tweet_id = total_tweets[0].id

        # Query further back in batches until exceed threshold
        # or there is no more data to be had
        while len(total_tweets) < threshold:
            tweets = twitter_user[0].timeline(count=200,
                                        exclude_replies=True,
                                        include_rts=False,
                                        tweet_mode='extended',
                                        max_id=oldest_tweet,
                                        since_id=last_tweet)

            # No more so exit loop
            if len(tweets) == 0:
                break
            
            total_tweets += tweets
            oldest_tweet = tweets[-1].id - 1
            tweets_found = len(total_tweets)
            print(f'{tweets_found} tweets found for {twitter_user[0].screen_name}.')

        # Get embeddings and insert into tweet table
        for tweet in total_tweets:
            tweets_found -= 1
            Que.put({'user': twitter_user[0].screen_name, 
                    'count': tweets_found,
                    'status': 0},
                    block=False)

            embedding = Basilica.embed_sentence(tweet.full_text, 
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                            tweet=tweet.full_text[:300],
                            embedding=embedding)
            twitter_user[1].tweet.append(db_tweet)
            db.session.add(db_tweet)

        db.session.commit()
    
    Que.put({'user': twitter_user[0].screen_name, 
                'count': len(total_tweets),
                'status': 1},
                block=False)
    return


def listTweets(tweets):
    html = '<div>'
    for tweet in tweets:
        html += \
            f'<p class="stack"><li>{tweet.tweet}</li></p>'
    html += '</div>'
    return html
