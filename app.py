"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

import os
from flask import Flask, render_template, jsonify, redirect, session, request
from models import db, connect_db, User, Equipment, Target, Exercise, BlockedExercise
from forms import RegisterForm, LoginForm, SettingsForm
from sqlalchemy.exc import IntegrityError
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///movement_breaks')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = config.secret_key

connect_db(app)

@app.route('/')
def show_timer():
    """Display timer/home page"""
    user = User.query.get(session['user_id']) if 'user_id' in session else None
    return render_template('timer.html', user=user) 

@app.route('/exercises')
def get_exercises():
    """
    Return query status and exercises, filtering for user's preferences if logged in.

    Users that are not logged in will only be shown body weight exercises.

    exercises_found indicates whether exercises were found that fulfill all user preferences.
    If exercises_found is False, all body weight exercises will be returned as a default instead.
    """
    bodyweight_id = Equipment.query.filter(Equipment.name == 'body weight').one().id
    exercises_found = True

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            # Filter exercises for user equipment preferences, default to bodyweight only
            equip_ids = [equip.id for equip in user.equipment] if user.equipment else [bodyweight_id]
            exercise_query = Exercise.query.filter(Exercise.equipment_id.in_(equip_ids))

            # Filter out blocked exercises
            blocked_ids = [equip.id for equip in user.blocked_exercises]
            exercise_query = exercise_query.filter(Exercise.id.not_in(blocked_ids))

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
    """Register new user, redirecting to home page on success"""
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
    """Authenticate user details and handle login"""

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
    """Handle logout"""

    session.pop('user_id')
    return redirect('/')

@app.route('/settings', methods=['GET', 'POST'])
def change_settings():
    """
    Change user settings for timer length and exercise preferences.

    Requires logged in user, otherwise redirects to home page. 
    """

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
    
@app.route('/users/<int:user_id>/block', methods=['POST'])
def block_exercise(user_id):
    """
    Add an exercise to user's blocked exercises list
    """

    # Verify that user is logged in and adding a block to their own account
    if 'user_id' in session and user_id == session['user_id']:
        block = BlockedExercise(user_id=user_id, exercise_id=request.json.get('exercise_id'))
        db.session.add(block)
        db.session.commit()
        return (jsonify(message="Blocked exercise"), 201)
    return (jsonify(message="Unauthorized"), 401)
