from flask import Blueprint, render_template, request

from web_app.db.db_model import db, User


twitoff_routes = Blueprint('twitoff_routes', __name__)

@twitoff_routes.route('/users')
def users():
    html =  '''
            <H3>Not Yet Implemented</H3>
            <a href='index'>Back...</a>
            '''
    return html

@twitoff_routes.route('/add_user')
def add_user():
    return render_template("add_user.html")

@twitoff_routes.route('/create_user', methods=['POST'])
def create_user():
    info = dict(request.form)
    new_user = User(user=info['User'], followers=info['Followers'])
    db.session.add(new_user)
    db.session.commit()
    html = f'''
               <p>You added {dict(request.form)}</p>
               <a href='index'>Back...</a>
            '''
    return html
               

