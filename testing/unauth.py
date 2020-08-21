import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from app import app
from constants import load_challenge_dict

challenge_dict = load_challenge_dict()

class UnauthRoutesTesting(unittest.TestCase):

	# Ensure home page loads correct data
	def test_index_page_loads(self):
		tester = app.test_client(self)
		response = tester.get('/', content_type='html/text')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Challenge Tracker', response.data)
		self.assertIn(b'Sign Up', response.data)
		self.assertIn(b'Login', response.data)
		self.assertIn(b'Leaderboard', response.data)

	# Ensure login page loads correct data
	def test_login_page_loads(self):
		tester = app.test_client()
		response = tester.get('/login', content_type='html/text')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'<title> Login </title>', response.data)
		self.assertIn(b'username', response.data)
		self.assertIn(b'password', response.data)
		self.assertIn(b'Forgot Password?', response.data)
		self.assertIn(b'cancel', response.data)

	# Ensure unauth leaderboard w/out brackts loads correct data
	def test_leaderboard_form_loads(self):
		tester = app.test_client(self)
		response = tester.get('/leaderboard', content_type='html/text')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'<title> Leaderboard </title>', response.data)
		self.assertIn(b'Challenge', response.data)
		self.assertIn(b'Brackets', response.data)

	# Ensure unauth leaderboard w/ brackets loads correct data
	def test_leaderboard_brackets_page_loads(self):
		tester = app.test_client(self)
		response = tester.post(
			'/leaderboard', 
			data=dict(
				challenge=challenge_dict['time'][1],
				bracketswitch=True
			),
			follow_redirects=True
		)
		self.assertEqual(response.status_code, 200)
		if not b'There are no competitors for that challenge' in response.data:
			self.assertIn(b'<th>Place</th>', response.data)
			self.assertIn(b'<th>Name</th>', response.data)				
			self.assertIn(b'<th>Comment</th>', response.data)		
		self.assertIn(b'<a href="/leaderboard" class="btn">Pick a new challenge</a>', response.data)

		# Ensure unauth leaderboard w/out brackets loads correct data
	def test_leaderboard_no_brackets_page_loads(self):
		tester = app.test_client(self)
		challenge=challenge_dict['time'][1]
		response = tester.post(
			'/leaderboard', 
			data=dict(
				challenge=challenge,
				# bracketswitch=True
			),
			follow_redirects=True
		)
		self.assertEqual(response.status_code, 200)
		if b'There are no competitors for that challenge</p>' in response.data:
			self.assertIn(b'There are no competitors for that challenge</p>', response.data)
			return 
		self.assertIn(b'<th>Place</th>', response.data)
		self.assertIn(b'<th>Name</th>', response.data)				
		self.assertIn(b'<th>Comment</th>', response.data)
		
		self.assertIn(b'<a href="/leaderboard" class="btn">Pick a new challenge</a>', response.data)
			
	# Ensure signup page loads correct data
	def test_signup_page_loads(self):
		tester = app.test_client()
		response = tester.get('/signup', content_type='html/text')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'<title> Signup </title>', response.data)
		self.assertIn(b'First Name', response.data)
		self.assertIn(b'Last Name', response.data)
		self.assertIn(b'Gender', response.data)

	# Ensure signup page loads correct data
	def test_signup_page_loads(self):
		pass

