"""Models for Movement Breaks"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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