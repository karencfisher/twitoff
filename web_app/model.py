import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from web_app.db.db_model import db, User, Tweet
from web_app.twitter_off import Basilica


def predictUser(username1, username2, tweet_text):
    data = Tweet.query.join(User).with_entities(User.user, Tweet.embedding).\
        filter(User.user.in_((username1, username2))).all()
    X = [data[i][1] for i in range(len(data))]
    y = [data[i][0] for i in range(len(data))]

    le = LabelEncoder()
    y = le.fit_transform(y)

    clf = LogisticRegression(solver='lbfgs', max_iter=5000)
    clf.fit(X, y)

    embed = np.array(Basilica.embed_sentence(tweet_text, model='twitter'))
    x = embed.reshape(1, -1)
    result = clf.predict_proba(x)

    return np.squeeze(result), le.classes_
    
  