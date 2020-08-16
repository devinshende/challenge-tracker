import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from app import app

'''
IMPORTANT: all test functions MUST begin with 'test' or else unittest does not pick it up
'''

class IndexTesting(unittest.TestCase):

	# Ensure that flask was set up correctly
	def test_index(self):
		tester = app.test_client(self)
		response = tester.get('/login', content_type='html/text')
		self.assertEqual(response.status_code, 200)

	# Ensure home page returns correct data
	def test_home_page_loads(self):
		tester = app.test_client(self)
		response = tester.get('/',content_type='html/text')
		self.assertTrue(b'Challenge Tracker' in response.data)
		self.assertTrue(b'Sign Up' in response.data)
		self.assertTrue(b'Login' in response.data)
		self.assertIn(b'Leaderboard', response.data)

	# Ensure login behaves correctly with correct credentials
	# def test_correct_login(self):
	# 	tester = app.test_client(self)
	# 	response = tester.post(
	# 		'/login',
	# 		data=dict(username="VALID USERNAME",password="VALID PASSWORD"),
	# 		follow_redirects=True
	# 	)
	# 	self.assertIn(b'Welcome,', response.data)

	# # Ensure login behaves with incorrect password
	# def test_incorrect_login_password(self):
	# 	tester = app.test_client(self)
	# 	response = tester.post(
	# 		'/login',
	# 		data=dict(username="ds",password="hello world"),
	# 		follow_redirects=True
	# 	)
	# 	self.assertIn(b'Incorrect Password', response.data)
		
	# # Ensure login behaves with incorrect username
	# def test_incorrect_login_username(self):
	# 	tester = app.test_client(self)
	# 	response = tester.post(
	# 		'/login',
	# 		data=dict(username="jafadfladfjafa",password="hello world"),
	# 		follow_redirects=True
	# 	)
	# 	self.assertIn(b'Invalid Username', response.data)


if __name__ == '__main__':
	unittest.main()
