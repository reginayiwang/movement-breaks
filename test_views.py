"""Views tests"""

# Run with FLASK_ENV=production python -m unittest test_views.py

import os 
from unittest import TestCase
from models import db, User, Equipment, Target, Exercise

os.environ['DATABASE_URL'] = "postgresql:///movement_test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ViewsTestCase(TestCase):
    """Test views for Movement Breaks app"""

    def setUp(self):
        """Clear data, add sample data"""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        target_abs= Target(name="abs")
        target_biceps = Target(name="biceps")
        equip_bodyweight = Equipment(name="body weight")
        equip_dumbbell = Equipment(name="dumbbell")
        db.session.add_all([target_abs, target_biceps, equip_bodyweight, equip_dumbbell])
        db.session.commit()

        bicep_curl = Exercise(name="bicep curl", gif_url="curl.url", instructions=["Do a bicep curl"],
                             target_id=target_biceps.id, equipment_id=equip_dumbbell.id)
        sit_up = Exercise(name="sit-up", gif_url="sit-up.url", instructions=["Do a sit-up"],
                             target_id=target_abs.id, equipment_id=equip_bodyweight.id)
        chin_up = Exercise(name="chin-up", gif_url="chin-up.url", instructions=["Do a chin-up"],
                             target_id=target_biceps.id, equipment_id=equip_bodyweight.id)
        db.session.add_all([bicep_curl, sit_up, chin_up])
        db.session.commit()

        user = User.register(username="test", password="password")
        user.targets.append(target_biceps)
        user.equipment = [equip_bodyweight, equip_dumbbell]
        db.session.add(user)
        db.session.commit()

        self.abs_id = target_abs.id
        self.bodyweight_id = equip_bodyweight.id
        self.chinup_id = chin_up.id
        self.user_id = user.id
        self.user = user

    def tearDown(self):
        db.session.rollback()

    def test_homepage_logged_in(self):
        """Does homepage show up correctly if not logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = self.client.get('/')
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/logout">', data)
            self.assertIn('Settings', data)

    def test_homepage_logged_out(self):
        """Does homepage show up correctly if not logged in?"""
        
        with self.client as c:
            response = c.get('/')
            data = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/login">', data)
            self.assertNotIn('Settings', data)

    def test_register_form(self):
        """Does registration form work?"""
        
        with self.client as c:
            response = c.get('/register')
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h1 class="h1">Register</h1>', data)

    def test_register_user(self):
        """Does user registration work?"""

        with self.client as c:
            response = self.client.post('/register', data={
                'username': 'test2',
                'password': 'password'
            }, follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/logout">', data)

    def test_register_existing_user(self):
        """Does registration fail for existing username?"""

        with self.client as c:
            response = self.client.post('/register', data={
                'username': 'test',
                'password': 'password'
            })
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Username already exists.', data)

    def test_login_form(self):
        """Does login form work?"""
        
        with self.client as c:
            response = c.get('/login')
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h1 class="h1">Log in</h1>', data)

    def test_valid_login(self):
        """Does login work for valid username/password combination?""" 

        with self.client as c:
            response = self.client.post('/login', data={
                'username': 'test',
                'password': 'password'
            }, follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/logout">', data)

    def test_invalid_login(self):
        """Does login fail for invalid username/password combination?"""

        with self.client as c:
            response = self.client.post('/login', data={
                'username': 'test',
                'password': 'pw'
            })
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('>Incorrect username/password combination.', data)    

    def test_logout(self):
        """Does logout work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = c.get('/logout', follow_redirects=True)
            data = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/login">', data)

    def test_get_exercises(self):
        """Does retrieving exercises when not logged in return all body weight exercises?"""
        
        with self.client as c:
            response = c.get('/exercises')
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('chin-up', data)
            self.assertIn('sit-up', data)
            self.assertNotIn('bicep curl', data)

    def test_get_exercises_logged_in(self):
        """Does retrieving exercises when logged in filter based on user preferences?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = c.get('/exercises')
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('chin-up', data)
            self.assertNotIn('sit-up', data)
            self.assertIn('bicep curl', data)

    def test_update_settings(self):
        """Does updating settings work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id
            
            response = c.post('/settings', data={
                'work_length': 45,
                'break_length': 10
            }, follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('45', data)
            self.assertIn('10', data)

    def test_settings_form_logged_out(self):
        """Does settings form redirect to home page if logged out?"""

        with self.client as c:
            response = c.get('/settings', follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)        
            self.assertIn('id="timer"', data)
            self.assertIn('<a class="nav-link" href="/login">', data)

    def test_block_exercise(self):
        """Does blocking exercise work?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = c.post(f'/users/{self.user_id}/block', json={'exercise_id': self.chinup_id}, follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 201)
            self.assertIn('Blocked exercise', data)

    def test_block_exercise_logged_out(self):
        """Does blocking exercise fail when logged out?"""

        with self.client as c:
            response = c.post(f'/users/{self.user_id}/block', json={'exercise_id': self.chinup_id}, follow_redirects=True)
            data = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 401)
            self.assertIn('Unauthorized', data)


    
    
