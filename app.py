"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

from flask import Flask, render_template, jsonify, abort, redirect, session, request, flash
from models import db, connect_db, User, Equipment, Target, Exercise
from forms import RegisterForm, LoginForm, SettingsForm
from sqlalchemy.exc import IntegrityError
import requests
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movement_breaks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
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
    bodyweight_id = Equipment.query.filter(Equipment.name == 'body weight').one().id
    exercises_found = True

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            # Filter exercises for user equipment preferences, default to body weight only
            equip_ids = [equip.id for equip in user.equipment] if user.equipment else [bodyweight_id]
            exercise_query = Exercise.query.filter(Exercise.equipment_id.in_(equip_ids))

            # Filter for user target preferences if present
            target_ids = [target.id for target in user.targets]
            if target_ids:
                exercise_query = exercise_query.filter(Exercise.target_id.in_(target_ids))
            
            exercises = [exercise.serialize() for exercise in exercise_query.all()]
            
            if exercises:
                return jsonify({'exercises_found': exercises_found,
                                'exercises': exercises})
            else:
                exercises_found = False

    # Return body weight exercises if not logged in or if filtering failed to retrieve exercises
    exercises = [exercise.serialize() for exercise in Equipment.query.get(bodyweight_id).exercises]
    return jsonify({'exercises_found': exercises_found,
                    'exercises': exercises})

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
        user = User.query.get(session['user_id'])
        form = SettingsForm()
        form.equipment.choices = [(equipment.id, equipment.name) for equipment in Equipment.query.all()]
        form.targets.choices = [(target.id, target.name) for target in Target.query.all()]

        # Prepopulate form with current settings. This is done manually because passing user to obj does not work for multiselect fields
        if request.method == 'GET':
            form.equipment.default = [equipment.id for equipment in user.equipment]
            form.targets.default = [target.id for target in user.targets]
            form.process()

            # form.process() clears out other prepopulated fields, so we populate these after
            form.work_length.data = user.work_length
            form.break_length.data = user.break_length

        if form.validate_on_submit():
            user.work_length = form.work_length.data
            user.break_length = form.break_length.data

            for selection in form.equipment.data:
                equipment = Equipment.query.get(selection)
                user.equipment = []
                user.equipment.append(equipment)
            
            for selection in form.targets.data:
                target = Target.query.get(selection)
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