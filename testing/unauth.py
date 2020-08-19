import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from app import app

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

	# Ensure unauth leaderboard loads correct data
	def test_leaderboard_page_loads(self):
		tester = app.test_client(self)
		response = tester.get('/leaderboard', content_type='html/text')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'<title> Leaderboard </title>', response.data)
		self.assertIn(b'Challenge', response.data)
		self.assertIn(b'Brackets', response.data)

