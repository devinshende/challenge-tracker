import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from app import app

'''
IMPORTANT: all test functions MUST begin with 'test' or else unittest does not pick it up
'''
# login tests
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

# import all the testing files
from unauth import UnauthRoutesTesting

if __name__ == '__main__':
	unittest.main()
