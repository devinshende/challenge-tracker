import unittest
import sys, os; sys.path.insert(1, os.path.join(sys.path[0], '..'))
# allows importing from parent folder
from utils import *

class HelperFunctionsTesting(unittest.TestCase):

	# Ensure to_name_case function works as intended
	def test_to_name_case(self):
		self.assertEqual(
			to_name_case('kevin'),
			'Kevin'
		)
		self.assertEqual(
			to_name_case('keVin'),
			'Kevin'
		)
		self.assertEqual(
			to_name_case('kevin '),
			'Kevin '
		)
		self.assertEqual(
			to_name_case('KEviN'),
			'Kevin'
		)

