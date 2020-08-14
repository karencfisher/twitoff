import html

import numpy as np
from flask import Blueprint, render_template, request

from web_app.db.db_model import db, User, Tweet
from web_app.twitter_off import add_twitter_user, listTweets, updateTweets
from web_app.model import predictUser


twitoff_routes = Blueprint('twitoff_routes', __name__)

@twitoff_routes.route('/')
def users():
    users=User.query.all() 
    return render_template("base.html", users=users, message='')

@twitoff_routes.route('/user', methods=['POST'])
def user():
    user = dict(request.form)['User']
    tweets = Tweet.query.join(User).filter(User.user == user).\
        order_by(Tweet.id.desc())
    name = User.query.filter_by(user=user).first().name
    users=User.query.all()
    return render_template("base.html", users=users, message='',
                           tweets=listTweets(tweets), username=user,
                           name=name)

@twitoff_routes.route('/create_user', methods=['POST'])
def create_user():
    info = dict(request.form)
    try:
        already_exists = add_twitter_user(info['User'])
    except Exception as err:
        print(f"Error adding {info['User']}: {err}")
        return errorMsg(err)
    else:
        if already_exists:
            message = f"{info['User']} is already in the database."
            tweets = Tweet.query.join(User).filter(User.user == user).\
                order_by(Tweet.id.desc())
            users=User.query.all()
            return render_template("base.html", users=users, message=message,
                           tweets=listTweets(tweets), username=info['User'],
                           name=name)
        else:
            return render_template("waiting.html", count_tweets=0, 
                                   user=info['User'])
    

@twitoff_routes.route('/compare', methods=['POST'])
def compare():
    info = dict(request.form)
    user1 = info['user1']
    user2 = info['user2']
    text = html.unescape(info['tweet_text'])
    if user1 == user2:
        verdict = 'Choose different users to compare!'
        message = 'Choose different users to compare!'
    else:
        result, contest = predictUser(user1, user2, text)
        winner = contest[np.argmax(result)]
        score = round(result[np.argmax(result)], 2)
        name = User.query.filter_by(user=winner).first().name
        verdict = \
            f'Probability is that {name} ({winner}) said this by {score * 100} %'
        message = ''

    users=User.query.all()
    return render_template("base.html", users=users, message=message,
                           result=verdict, tweet=text,
                           username1=user1, username2=user2)

@twitoff_routes.route('/update')
def update():
    results = updateTweets()
    result = '<div>'
    for key in results.keys():
        result += f'<li>{key} added {results[key]} tweets</li>'
    result += '</div>'

    users=User.query.all()
    return render_template("base.html", users=users, message='',
                            updates=result)

@twitoff_routes.route('/waiting/<username>')
def waiting(username):
    count_tweets = 0
    try:
        tweets = Tweet.query.join(User).filter(User.user == info['User']).\
            count()
        count_tweets = tweets
    except:
        pass
    return render_template("waiting.html", count_tweets=count_tweets,
                           user=username))
               

def errorMsg(err):
    message = f'An error occured. {err}'
    users=User.query.all() 
    return render_template("base.html", users=users, message=message)
    

