from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKeyConstraint

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    username = db.Column(db.String(20), 
                   primary_key=True, 
                   unique=True
                   )

    password = db.Column(db.Text, 
                         nullable=False
                         )

    email = db.Column(db.String(50), 
                         nullable=False,
                         unique=True
                         )

    first_name = db.Column(db.String(30), 
                         nullable=False
                         )

    last_name = db.Column(db.String(30), 
                         nullable=False
                         )

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Registering New User w/hashed password & Return User"""
        hashed = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls,username,pwd):
        """Validate that user exists & password is correct
        Return user if valid; els return False"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

class Feedback(db.Model):
    """Not Sure what Im making this yet"""

    __tablename__ = "feedbacks"

    id = db.Column( db.Integer, 
                    primary_key=True, 
                    autoincrement=True
                    )

    title = db.Column(db.String(100),
                      nullable=False
                        )

    content = db.Column( db.Text,
                         nullable=False
                         )
        
    username = db.Column( db.Text, 
                        db.ForeignKey('users.username'),
                        nullable=False
                        )

    user = db.relationship('User',
                            backref='feedbacks'
                            )