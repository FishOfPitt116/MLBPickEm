import os, json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import statsapi

from models import db, User

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
))

app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent=True)
SQLALCHEMY_TRACK_MODIFICATIONS = True

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    print("Database Tables Initialized.")

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
            return redirect(url_for('open_rooms'))
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

@app.route('/picks')
def picks(date):
    # if date == None:
    #     return redirect(url_for('picks', date=datetime.today().date()))
    pass

@app.route('/leaderboards')
def leaderboards():
    pass