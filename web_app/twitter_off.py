from os import getenv

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


def add_twitter_user(username, threshold=200):
    try:
        # Get user information
        twitter_user = Twitter.get_user(username)
    except tweepy.TweepError as err:
        raise Exception(f'{username} not found.')

    # Check if it already exists in the DB
    if User.query.get(twitter_user.id) is not None:
        return 0

    db_user = User(id=twitter_user.id, user=username,
                    name=twitter_user.name)
    db.session.add(db_user)
    
    # Get first batch of tweets
    total_tweets = twitter_user.timeline(count=50,
                                    exclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended')

    # Get oldest and newest tweets
    oldest_tweet = total_tweets[-1].id - 1
    db_user.newest_tweet_id = total_tweets[0].id

    # Query further back in batches until exceed threshold
    # or there is no more data to be had
    while len(total_tweets) < threshold:
        tweets = twitter_user.timeline(count=50,
                                    exclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended',
                                    max_id=oldest_tweet)

        # No more so exit loop
        if len(tweets) == 0:
            break

        total_tweets += tweets
        oldest_tweet = tweets[-1].id - 1

    # Get embeddings and insert into tweet table
    for tweet in total_tweets:
        embedding = Basilica.embed_sentence(tweet.full_text, 
                                            model='twitter')
        db_tweet = Tweet(id=tweet.id,
                        tweet=tweet.full_text[:300],
                        embedding=embedding)
        db_user.tweet.append(db_tweet)
        db.session.add(db_tweet)

    db.session.commit()
    return len(total_tweets)
    

def updateTweets():
    users = User.query.all()
    updates = {}
    for user in users:
        updates[user.user] = 0
        last_tweet = user.newest_tweet_id

        # Get first new batch
        twitter_user = Twitter.get_user(user.user)
        total_tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=last_tweet)
        
        # If no new tweets for user, go to the next user
        if len(total_tweets) == 0:
            continue

        # Cache the newest and oldest
        user.newest_tweet_id = total_tweets[0].id
        oldest_tweet = total_tweets[-1].id - 1

        for tweet in total_tweets:
            # Extra caution not to duplicate tweets and trigger DB exception
            if tweet.id <= last_tweet:
                break

            # get embedding and add to DB
            embedding = Basilica.embed_sentence(tweet.full_text, 
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                             tweet=tweet.full_text[:300],
                             embedding=embedding)
            user.tweet.append(db_tweet)
            db.session.add(db_tweet)

        updates[user.user] = len(total_tweets)

    db.session.commit()
    return updates


def listTweets(tweets):
    html = '<div>'
    for tweet in tweets:
        html += \
            f'<p class="stack"><li>{tweet.tweet}</li></p>'
    html += '</div>'
    return html
