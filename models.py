from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    username = db.Column(db.String(24), primary_key=True)
    pw_hash = db.Column(db.String(64), nullable=False)

    def __init__(self, username, pw_hash):
        self.username = username
        self.pw_hash = pw_hash

    def __repr__(self):
        return f'<username {self.username}, password {self.password}>'

