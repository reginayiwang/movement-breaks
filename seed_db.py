"""Seed database with equipment and exercise targets from API"""

from app import app
import requests
import sys
from models import db, Equipment, Target, Exercise
import config

base_url = 'https://exercisedb.p.rapidapi.com/exercises'
headers = {
    'x-rapidapi-host': 'exercisedb.p.rapidapi.com',
    'x-rapidapi-key': config.api_key
}

db.drop_all()
db.create_all()

equipment = []
targets = []
exercises = []

try:
    equip_res = requests.get(f"{base_url}/equipmentList", headers=headers)
    for equip in equip_res.json():
        equipment.append(Equipment(name=equip))

    target_res = requests.get(f"{base_url}/targetList", headers=headers)
    for target in target_res.json():
        targets.append(Target(name=target))

    exercise_res = requests.get(f"{base_url}?limit=0", headers=headers).json()
except:
    print("Could not get data from API.")
    sys.exit()

db.session.add_all(equipment)
db.session.add_all(targets)
db.session.commit()

for exercise in exercise_res:
    equipment = Equipment.query.filter_by(name=exercise['equipment']).one()
    target = Target.query.filter_by(name=exercise['target']).one()
    new_exercise = Exercise(name=exercise['name'], gif_url=exercise['gifUrl'], instructions=exercise['instructions'], equipment_id=equipment.id, target_id=target.id)
    exercises.append(new_exercise)

db.session.add_all(exercises)
db.session.commit()