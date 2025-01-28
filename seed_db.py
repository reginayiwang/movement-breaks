"""Seed database with equipment and exercise targets from API"""

import requests
import sys
from models import db, Equipment, Target
import config

base_url = 'https://exercisedb.p.rapidapi.com/exercises'
headers = {
    'x-rapidapi-host': 'exercisedb.p.rapidapi.com',
    'x-rapidapi-key': config.api_key
}

def seed_db():
    db.drop_all()
    db.create_all()

    equipment = []
    targets = []

    try:
        equip_res = requests.get(f"{base_url}/equipmentList", headers=headers)
        for equip in equip_res.json():
            equipment.append(Equipment(name=equip))

        target_res = requests.get(f"{base_url}/targetList", headers=headers)
        for target in target_res.json():
            targets.append(Target(name=target))
    except:
        print("Could not get data from API.")
        sys.exit()

    db.session.add_all(equipment)
    db.session.add_all(targets)
    db.session.commit()