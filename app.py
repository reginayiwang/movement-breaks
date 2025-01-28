"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

from flask import Flask, render_template, jsonify, abort, redirect, session
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError
import requests
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movement_breaks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = config.secret_key

base_url = 'https://exercisedb.p.rapidapi.com/exercises'
headers = {
    'x-rapidapi-host': 'exercisedb.p.rapidapi.com',
    'x-rapidapi-key': config.api_key
}

connect_db(app)

@app.route('/')
def show_timer():
    return render_template('timer.html') 

@app.route('/exercises')
def get_exercises():
    params = {
        'limit': 0
    }
    try:
        exercises = requests.get(f"{base_url}/equipment/body weight", headers=headers, params=params)
        return jsonify(exercises.json())
    except:
        abort(500)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already exists. Please try another.')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id 
        return redirect('/')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.login(username, password)
        if user:
            session['user_id'] = user.id
            return redirect('/')
        form.password.errors.append('Incorrect username/password combination. Please try again.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/')

@app.errorhandler(500)
def server_error(err):
    return "Sorry, something went wrong", 500