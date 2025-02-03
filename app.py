"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

from flask import Flask, render_template, jsonify, abort, redirect, session
from models import db, connect_db, User, Equipment, Target
from forms import RegisterForm, LoginForm, SettingsForm
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
    user = User.query.get(session['user_id']) if 'user_id' in session else None
    return render_template('timer.html', user=user) 

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

@app.route('/settings', methods=['GET', 'POST'])
def change_settings():
    if 'user_id' in session:
        form = SettingsForm()
        form.equipment.choices = []
        form.target.choices = []

        for equipment in Equipment.query.all():
            form.equipment.choices.append(equipment.name)

        for target in Target.query.all():
            form.target.choices.append(target.name)

        if form.validate_on_submit():
            user = User.query.get(session['user_id'])
            user.work_length = form.work_length.data
            user.break_length = form.break_length.data

            for selection in form.equipment.data:
                equipment = Equipment.query.filter_by(name=selection).one()
                user.equipment = []
                user.equipment.append(equipment)
            
            for selection in form.target.data:
                target = Target.query.filter_by(name=selection).one()
                user.targets = []
                user.targets.append(target)

            db.session.add(user)
            db.session.commit()
        
        return render_template('settings.html', form=form)
    else:
        return redirect('/')

@app.errorhandler(500)
def server_error(err):
    return "Sorry, something went wrong", 500