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

class Team(db.Model):
    name = db.Column(db.String(52), primary_key=True)

    def __init__(self, name):
        self.name = name

class Game(db.Model):
    game_id = db.Column(db.String(12), primary_key=True)
    away_id = db.Column(db.String(52), db.ForeignKey('team.name'))
    away_pitcher = db.Column(db.String(64))
    home_id = db.Column(db.String(52), db.ForeignKey('team.name'))
    home_pitcher = db.Column(db.String(64))
    status = db.Column(db.String(24), nullable=False)
    away_score = db.Column(db.Integer)
    home_score = db.Column(db.Integer)
    inning = db.Column(db.Integer)

    def __init__(self, game_id, away_id, away_pitcher, home_id, home_pitcher, status, away_score, home_score, inning):
        self.game_id = game_id
        self.away_id = away_id
        self.away_pitcher = away_pitcher
        self.home_id = home_id
        self.home_pitcher = home_pitcher
        self.status = status
        self.away_score = away_score
        self.home_score = home_score
        self.inning = inning

class Pick(db.Model):
    username = db.Column(db.String(24), db.ForeignKey('user.username'), primary_key=True)
    game_id = db.Column(db.String(12), db.ForeignKey('game.game_id'), primary_key=True)
    pick = db.Column(db.String(52), db.ForeignKey('team.name'))

    def __init__(self, username, game_id, pick):
        self.username = username
        self.game_id = game_id
        self.pick = pick