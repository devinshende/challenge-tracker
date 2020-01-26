import pickle, os
from datetime import datetime

class Entry(object):
	"""class to store data about a user's time entry on a certain obstacle"""
	def __init__(self, initlist):
		self.initlist = initlist
		self.score, date, self.comment = initlist
		
		if type(self.score) != float:
			if type(self.score) != int:
				raise ValueError('score must be of type float or int')

		# 8.24.19
		d = date.split('.')
		self.date = datetime(year=int(d[2]), month=int(d[0]), day=int(d[1]))
		if repr(type(self.date)) != "<class 'datetime.datetime'>":
			raise ValueError('date provided to entry() must be of class <class \'datetime.datetime\'>')
		
		if self.comment == None:
			self.comment = ''
		if type(self.comment) != str:
			raise ValueError('comment must be of type <str>')

	def __repr__(self):
		date = self.date.strftime("%B %d %Y")
		return f'--Entry score={self.score}, date={date}, comment="{self.comment}--'

	def format_date(self):
		date = self.date.strftime("%B %d %Y")
		return date

	def to_json(self):
		return self.initlist

class ChallengeTypes(object):
	"""contains all the available options for types of challenges"""
	reps = 'reps'
	laps = 'laps'
	time = 'time'

def write_challenges(data):
	with open('database/challenges.pickle','wb') as file:
		pickle.dump(data,file)

def read_challenges():
	if os.path.getsize('database/challenges.pickle') > 0:   
		with open('database/challenges.pickle','rb') as file:
			x = pickle.load(file)
		return x
	else:
		print('pickle file is empty')
		return {}