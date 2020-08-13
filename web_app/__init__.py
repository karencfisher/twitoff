from os import getenv

from flask import Flask
from dotenv import load_dotenv

from web_app.db.db_model import db
from web_app.routes.twitoff_routes import twitoff_routes

load_dotenv()
DATABASE_URI = 'sqlite:///db\\twitoff_db.sqlite'
#DB_URL = getenv('DB_URL')
DB_URL = 'postgres://lrelfakuvrkuui:e34cfbe7bc3ce4cf7fca0603346129f947755a11cd0bb638c7c08c8303d21101@ec2-184-73-249-9.compute-1.amazonaws.com:5432/dbj1kjrvlimh7n'


def create_app():
    print('Initializing...')
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    #app.register_blueprint(home_routes)
    app.register_blueprint(twitoff_routes)
    return app


if __name__ == '__main__':
    print('Main...')
    my_app = create_app()
    my_app.run(debug=True)
