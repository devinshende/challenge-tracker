import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from app import app

class FlaskTestCase(unittest.TestCase):

	# Ensure home page returns correct data
	def test_(self):
		tester = app.test_client(self)
		response = tester.get('/',content_type='html/text')