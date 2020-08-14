from os import getenv

from flask import Flask
from dotenv import load_dotenv

from web_app.db.db_model import db
from web_app.routes.twitoff_routes import twitoff_routes

load_dotenv()
DATABASE_URI = 'sqlite:///db\\twitoff_db.sqlite'
DATABASE_URL = getenv('DATABASE_URL')


def create_app():
    print('Initializing...')
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    db.app = app

    #app.register_blueprint(home_routes)
    app.register_blueprint(twitoff_routes)
    return app


if __name__ == '__main__':
    print('Main...')
    my_app = create_app()
    my_app.run(debug=True)
