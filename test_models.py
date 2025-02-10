"""Database tests"""

# Run with python -m unittest test_models.py

import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase

from models import db, User, Exercise, Equipment, Target, BlockedExercise

os.environ['DATABASE_URL'] = "postgresql:///movement_test"

from app import app

db.create_all()

class ExerciseModelTestCase(TestCase):
    """Test Exercise and related models"""

    def setUp(self):
        """Clear data before each test"""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_target_model(self):
        """Does basic Target model work?"""
        target = Target(name="abs")
        db.session.add(target)
        db.session.commit()

        self.assertIsNotNone(target.id)

    def test_equipment_model(self):
        """Does basic Equipment model work?"""
        equipment = Equipment(name="bands")
        db.session.add(equipment)
        db.session.commit()

        self.assertIsNotNone(equipment.id)

    def test_exercise_model(self):
        """Does basic Exercise model work?"""
        exercise = Exercise(name="push-up", gif_url="someurl", instructions=["Do a push-up"])
        db.session.add(exercise)
        db.session.commit()
        
        self.assertIsNotNone(exercise.id)

    def test_exercise_relationships(self):
        """Do Exercise model's relationships to Equipment and Target work?"""
        target = Target(name="biceps")
        equipment = Equipment(name="dumbbell")

        db.session.add_all([target, equipment])
        db.session.commit()

        exercise = Exercise(name="bicep curl", gif_url="someurl", instructions=["Do a bicep curl"],
                            target_id=target.id, equipment_id=equipment.id)
        db.session.add(exercise)
        db.session.commit()
        
        self.assertEqual(exercise.target.name, "biceps")
        self.assertEqual(exercise.equipment.name, "dumbbell")
        self.assertEqual(len(target.exercises), 1)
        self.assertEqual(len(equipment.exercises), 1)


class UserModelTestCase(TestCase):
    """Test User model"""

    def setUp(self):
        """Clear data before each test, set up test user"""
        db.drop_all()
        db.create_all()

        user = User.register("test", "password")

        db.session.add(user)
        db.session.commit()

        self.user = user

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic User model work?"""
        user = User.register("test2", "password")
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.work_length, 60)
        self.assertEqual(user.break_length, 5)

    # Register tests
    def test_register(self):
        "Does register work for valid input?"
        user = User.register("test3", "password2")

        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user)
        self.assertTrue(user.password_hash.startswith('$2b$'))

    def test_register_taken_username(self):
        """Does register fail for existing username?"""
        repeat_user = User.register("test", "password")
        db.session.add(repeat_user)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_register_missing(self):
        """Does register fail for missing info?"""
        with self.assertRaises(ValueError):
            User.register("test4", None)

    # Login tests
    def test_valid_login(self):
        """Does login work for valid info?"""
        login_user = User.login(self.user.username, "password")
        self.assertEqual(self.user, login_user)

    def test_invalid_login(self):
        """Does login fail for invalid info?"""
        invalid_username = User.login("invalid_user", "password")
        invalid_password = User.login("testuser1", "invalid_password")

        self.assertFalse(invalid_username)
        self.assertFalse(invalid_password)
    
    # Exercise preference tests
    def test_preferences(self):
        """Do user Equipment and Target preferences work?"""
        equipment = Equipment(name="kettlebell")
        equipment2 = Equipment(name="body weight")
        target = Target(name="cardio")
        db.session.add_all([equipment, equipment2, target])
        db.session.commit()

        self.user.equipment.append(equipment)
        self.user.equipment.append(equipment2)
        self.user.targets.append(target)
        db.session.commit()

        self.assertIn(equipment, self.user.equipment)
        self.assertIn(equipment2, self.user.equipment)
        self.assertIn(target, self.user.targets)


    def test_blocked_exercises(self):
        """Does BlockedExercise work?"""
        exercise = Exercise(name="burpee", gif_url="someurl", instructions=["Do a burpee"])
        db.session.add(exercise)
        db.session.commit()

        block = BlockedExercise(user_id=self.user.id, exercise_id=exercise.id)
        db.session.add(block)
        db.session.commit()

        self.assertEqual(len(self.user.blocked_exercises), 1)
        self.assertEqual(self.user.blocked_exercises[0].id, exercise.id)