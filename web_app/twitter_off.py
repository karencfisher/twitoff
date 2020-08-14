from os import getenv

import basilica
import tweepy  
from dotenv import load_dotenv
from rq import Queue

from web_app.db.db_model import db, User, Tweet
from worker import conn


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
    # q = Queue(connection=conn)
    # q.enqueue(fetch_tweets, (twitter_user, db_user))
    fetch_tweets((twitter_user, db_user))
    return False


def updateTweets():
    users = User.query.all()
    updates = {}
    for user in users:
        updates[user.user] = 0
        last_tweet = user.newest_tweet_id
        twitter_user = Twitter.get_user(user.user)
        updates[user.user] = \
            fetch_tweets((twitter_user, user), last_tweet=last_tweet)

    return updates
    
    
def fetch_tweets(twitter_user, threshold=200, last_tweet=1):
    # Get first batch of tweets
    total_tweets = twitter_user[0].timeline(count=200,
                                    exclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended',
                                    since_id=last_tweet)

    # Get oldest and newest tweets
    tweets_found = len(total_tweets)
    print(f'{tweets_found} tweets found for {twitter_user[0].screen_name}.')
    if tweets_found == 0:
        return tweets_found    
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

    # Get embeddings and insert into tweet table
    for tweet in total_tweets:
        tweets_found -= 1
        if tweets_found % 10 == 0:
            print(f'{tweets_found} left to process.')
        embedding = Basilica.embed_sentence(tweet.full_text, 
                                            model='twitter')
        db_tweet = Tweet(id=tweet.id,
                        tweet=tweet.full_text[:300],
                        embedding=embedding)
        twitter_user[1].tweet.append(db_tweet)
        db.session.add(twitter_user[1])

    db.session.commit()
    return len(total_tweets)


def listTweets(tweets):
    html = '<div>'
    for tweet in tweets:
        html += \
            f'<p class="stack"><li>{tweet.tweet}</li></p>'
    html += '</div>'
    return html
