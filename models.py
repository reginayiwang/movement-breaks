"""Models for Movement Breaks"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    "User model"

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True)
    username = db.Column(db.String(20),
                         nullable=False,
                         unique=True)
    password_hash = db.Column(db.String(60), 
                              nullable=False)
    work_length = db.Column(db.Integer, default=60)
    break_length = db.Column(db.Integer, default=5)
    equipment = db.relationship('Equipment', secondary='equipment_preferences', cascade='all, delete')
    targets = db.relationship('Target', secondary='target_preferences', cascade='all, delete')

    @classmethod
    def register(cls, username, password):
        """Register new user"""

        password_hash = bcrypt.generate_password_hash(password).decode("utf8")
        return cls(username=username, password_hash=password_hash)
    
    @classmethod
    def login(cls, username, password):
        """Handle user authentication"""

        user = User.query.filter_by(username=username).one()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        else:
            return False

class Exercise(db.Model):
    "Exercise model"

    __tablename__ = "exercises"

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String())
    gif_url = db.Column(db.String())
    instructions = db.Column(db.ARRAY(db.String))
    equipment_id = db.Column(db.Integer,
                             db.ForeignKey('equipment.id'))
    target_id = db.Column(db.Integer,
                          db.ForeignKey('targets.id'))
    equipment = db.relationship('Equipment', backref='exercises')
    target = db.relationship('Target', backref='target')

    def serialize(self):
       """Return serialized Exercise"""
       return {
           'name': self.name,
           'gifUrl': self.gif_url,
           'instructions': self.instructions
       }

class Equipment(db.Model):
    "Equipment model"

    __tablename__ = "equipment"

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(30),
                     unique=True)

class Target(db.Model):
    "Target (exercise target body part/type) model"

    __tablename__ = "targets"

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(30),
                     unique=True)

class EquipmentPreferences(db.Model):
    "EquipmentPreference model"

    __tablename__ = "equipment_preferences" 

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), 
                        primary_key=True)
    equipment_id = db.Column(db.Integer,
                             db.ForeignKey('equipment.id'),
                             primary_key=True)
    
class TargetPreferences(db.Model):
    "TargetPreference model"

    __tablename__ = "target_preferences"

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id',),
                        primary_key=True)
    target_id = db.Column(db.Integer,
                       db.ForeignKey('targets.id'),
                       primary_key=True)