from flask import Blueprint, render_template, request

from web_app.db.db_model import db, User
from web_app.twitter_off import add_twitter_user


twitoff_routes = Blueprint('twitoff_routes', __name__)

@twitoff_routes.route('/')
def users():
    users=User.query.all() 
    return render_template("base.html", users=users, message='')

@twitoff_routes.route('/user/<name>')
def user(name):
    tweets = User.query.filter(User.user == name).one().tweet
    users=User.query.all()
    return render_template("base.html", users=users, message='')

@twitoff_routes.route('/create_user', methods=['POST'])
def create_user():
    info = dict(request.form)
    try:
        add_twitter_user(info['User'])
    except Exception as err:
        message = f"Error adding {info['User']}: {err}"
    else:
        tweets = User.query.filter(User.user == info['User']).one().tweet
        message = f"You added {info['User']} to users."
    users=User.query.all()
    return render_template("base.html", users=users, message=message)

@twitoff_routes.route('/compare', methods=['POST'])
def compare():
    message = 'Whoa, not there yet!'
    users=User.query.all()
    return render_template("base.html", users=users, message=message)

@twitoff_routes.route('/update')
def update():
    message = 'Whoa, not there yet!'
    users=User.query.all()
    return render_template("base.html", users=users, message=message)
               

