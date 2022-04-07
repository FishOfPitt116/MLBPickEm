import os, json, statsapi, maya
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models import db, User, Team, Game, Pick

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'game.db')
))

app.config.from_object(__name__)
app.config.from_envvar('GAME_SETTINGS', silent=True)
SQLALCHEMY_TRACK_MODIFICATIONS = True

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    for team in statsapi.get('teams', {'leagueIds' : 103})['teams']:
        db.session.add(Team(team['name']))
    for team in statsapi.get('teams', {'leagueIds' : 104})['teams']:
        db.session.add(Team(team['name']))
    db.session.commit()
    print("Database Tables Initialized. MLB teams added.")

@app.route('/')
def home():
    return render_template('base.html', today=datetime.today().date())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        if (user := User.query.filter_by(username=request.form['username']).first()) is None:
            error = 'Invalid Credentials'
        elif not check_password_hash(user.pw_hash, request.form['password']):
            error = 'Invalid Credentials'
        else:
            flash('You were logged in')
            session['user_id'] = user.username
            session['logged_in'] = True
            return redirect(url_for('picks', date=datetime.today().date()))
    return render_template('login.html', error=error, today=datetime.today().date())

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['username'] == None or request.form['username'] == '':
            error = 'Empty Username'
        elif User.query.filter_by(username=request.form['username']).first() != None:
            error = 'Username already exists'
        elif request.form['password'] == None or request.form['password'] == '':
            error = 'Empty Password'
        elif request.form['password'] != request.form['confirmpassword']:
            error = 'Password confirmation does not match'
        else:
            db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
            db.session.commit()
            flash('Registration successful.')
            return redirect(url_for('login'))
    return render_template('register.html', error=error, today=datetime.today().date())

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('home'))

@app.route('/picks/<date>', methods=['GET'])
def picks(date):
    games = []
    for game in statsapi.schedule(date):
        if (curr := Game.query.filter_by(game_id=game['game_id'])).first() == None:
            db.session.add(Game(game['game_id'], game['away_name'], game['away_probable_pitcher'], game['home_name'], game['home_probable_pitcher'], game['status'], game['away_score'], game['home_score'], game['current_inning']))
            curr = Game.query.filter_by(game_id=game['game_id']).first()
        games.append(curr)
    # if date == None:
    #     return redirect(url_for('picks', date=datetime.today().date().date()))
    return render_template('picks.html', date=date, today=datetime.today().date(), games=games)

@app.route('/nextday/<date>')
def next_day(date):
    date = datetime.strptime(date, '%Y-%m-%d').date()
    try:
        return redirect(url_for('picks', date=date.replace(day=date.day+1)))
    except ValueError:
        try:
            return redirect(url_for('picks', date=date.replace(day=1, month=date.month+1)))
        except ValueError:
            return redirect(url_for('picks', date=date))

@app.route('/prevday/<date>')
def prev_day(date):
    date = datetime.strptime(date, '%Y-%m-%d').date()
    try:
        return redirect(url_for('picks', date=date.replace(day=date.day-1)))
    except ValueError:
        new_month = date.month-1
        if new_month == 2:
            return redirect(url_for('picks', date=date.replace(day=28, month=new_month)))
        if new_month in [9, 4, 6, 11]:
            return redirect(url_for('picks', date=date.replace(day=30, month=new_month)))
        try:
            return redirect(url_for('picks', date=date.replace(day=31, month=new_month)))
        except ValueError:
            return redirect(url_for('picks', date=date))

@app.route('/leaderboards')
def leaderboards():
    pass