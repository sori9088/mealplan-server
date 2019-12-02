from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model) :
    __tablename__ = 'users'
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(256))
    email=db.Column(db.String(256),unique=True)
    password = db.Column(db.String(256))

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password) :
        return check_password_hash(self.password, password)

     def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated


