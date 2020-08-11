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
        count = add_twitter_user(info['User'])
    except Exception as err:
        print(f"Error adding {info['User']}: {err}")
        return errorMsg(err)
    else:
        tweets = Tweet.query.join(User).filter(User.user == info['User']).\
            order_by(Tweet.id.desc())
        name = User.query.filter_by(user=info['User']).first().name
        if count == 0:
            message = f"{info['User']} is already in the database."
        else:
            message = f"You added {info['User']} to users and {count} tweets."
    users=User.query.all()
    return render_template("base.html", users=users, message=message,
                           tweets=listTweets(tweets), username=info['User'],
                           name=name)

@twitoff_routes.route('/compare', methods=['POST'])
def compare():
    info = dict(request.form)
    user1 = info['user1']
    user2 = info['user2']
    result, contest = predictUser(user1, user2, info['tweet_text'])
    winner = contest[np.argmax(result)]
    score = round(result[np.argmax(result)], 2)
    name = User.query.filter_by(user=winner).first().name
    verdict = \
        f'Probability is that {name} ({winner}) said this by {score * 100} %'

    users=User.query.all()
    return render_template("base.html", users=users, message='',
                           result=verdict, tweet=info['tweet_text'],
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
               
def errorMsg(err):
    message = f'An error occured. {err}'
    users=User.query.all() 
    return render_template("base.html", users=users, message=message)
    

