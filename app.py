"""Flask app for Movement Breaks (productivity timer with guided exercise breaks)"""

from flask import Flask, render_template
from models import db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movement_breaks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

@app.route('/')
def show_timer():
    return render_template('timer.html') 