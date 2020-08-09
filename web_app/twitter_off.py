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


def add_twitter_user(username):
    try:
        twitter_user = Twitter.get_user(username)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, user=username, 
                        name=twitter_user.name))
        db.session.add(db_user)

        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        for tweet in tweets:
            embedding = Basilica.embed_sentence(tweet.full_text, 
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                             tweet=tweet.full_text[:300],
                             embedding=embedding)
            db_user.tweet.append(db_tweet)
            db.session.add(db_tweet)

    except Exception as err:
        print('Error processing {}: {}'.format(username, e))
        raise e

    else:
        db.session.commit()


def updateTweets():
    users = User.query.all()
    updates = {}
    for user in users:
        last_tweet = user.newest_tweet_id
        twitter_user = Twitter.get_user(user.user)
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=last_tweet)
        
        if tweets:
            user.newest_tweet_id = tweets[0].id
        updates[user.user] = len(tweets)

        for tweet in tweets:
            embedding = Basilica.embed_sentence(tweet.full_text, 
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                             tweet=tweet.full_text[:300],
                             embedding=embedding)
            user.tweet.append(db_tweet)
            db.session.add(db_tweet)
    db.session.commit()
    return updates


def listTweets(tweets):
    html = '<div>'
    for tweet in tweets:
        html += \
            f'<p class="stack"><li>{tweet.tweet}</li></p>'
    html += '</div>'
    return html
