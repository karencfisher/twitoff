from flask import Blueprint


home_routes = Blueprint('home_routes', __name__)

@home_routes.route('/')
@home_routes.route('/index')
def index():
    html = '''
            <a href='users'>View Users</a>
            <br>
            <a href='add_user'>Add User</a>
            <br>
            <a href='about'>About Me...</a>
            '''
    return html

@home_routes.route('/about')
def about():
    html = '''
            <H2>I am not telling you!</H2> 
            So go away
            <a href = 'index'>Ok, sorry to bother you</a>
            '''
    return html

