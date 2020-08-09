import numpy as np
from sklearn.linear_model import LogisticRegression

from web_app.db.db_model import db, User, Tweet
from web_app.log_regression import LogRegression
from web_app.twitter_off import Basilica


def predictUser(username1, username2, tweet_text):
    user1 = User.query.filter(User.user == username1).one()
    user2 = User.query.filter(User.user == username2).one()

    user1_embeds = \
        np.array([tweet.embedding for tweet in user1.tweet])
    user2_embeds = \
        np.array([tweet.embedding for tweet in user2.tweet])

    # X = np.vstack([user1_embeds, user2_embeds])
    X = np.vstack([user1_embeds, user2_embeds]).T

    y = np.concatenate([np.ones(len(user1.tweet)), 
                        np.zeros(len(user2.tweet))])
    y = y.reshape(1, -1)

    clf = LogRegression(0.01, 3000, verbose=0)
    # clf = LogisticRegression(solver='lbfgs', max_iter=5000)
    clf.fit(X, y)

    embed = np.array(Basilica.embed_sentence(tweet_text, model='twitter'))
    # x = embed.reshape(1, -1)
    x = embed.reshape(-1, 1)
    result = clf.predict(x)

    return np.squeeze(result)
    
  