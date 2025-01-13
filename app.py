"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

from flask import Flask, render_template, jsonify, abort
import requests
from models import db, connect_db
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movement_breaks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

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
        # print(exercises.json())
        # abort(500)
        return jsonify(exercises.json())
    except:
        abort(500)
    
@app.errorhandler(500)
def server_error(err):
    return "Sorry, something went wrong", 500