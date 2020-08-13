from flask import Flask

from web_app.db.db_model import db
from web_app.routes.twitoff_routes import twitoff_routes


DATABASE_URI = 'sqlite:///db\\twitoff_db.sqlite'

def create_app():
    print('Initializing...')
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    #app.register_blueprint(home_routes)
    app.register_blueprint(twitoff_routes)
    return app


if __name__ == '__main__':
    print('Main...')
    my_app = create_app()
    my_app.run(debug=True)
