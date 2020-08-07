from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.String(128), nullable=False)
    newest_tweet_id = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f'<User {self.id} {self.name}>'


class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    tweet = db.Column(db.String(300), nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tweet', lazy=True))

    def __repr__(self):
        return f'<Tweet {self.tweet}>'