import pickle

class Entry(object):
	"""class to store data about a user's time entry on a certain obstacle"""
	def __init__(self, score, date, comment):
		if type(score) != float:
			if type(score) != int:
				raise ValueError('score must be of type float or int')
		self.score = float(score)
		self.date = date
		if repr(type(self.date)) != "<class 'datetime.datetime'>":
			raise ValueError('date provided to entry() must be of class <class \'datetime.datetime\'>')
		self.date_str = self.date.strftime("%B %dth, %Y")
		self.comment = comment
		if self.comment == None:
			self.comment = ''
		if type(self.comment) != str:
			raise ValueError('comment must be of type <str>')

	def __repr__(self):
		date = self.date.strftime("%B %d %Y")
		return f'--Entry score={self.score}, date={date}, comment="{self.comment}--'

def write_challenges(data):
	with open('database/challenges.pickle','wb') as file:
		pickle.dump(data,file)

def read_challenges():
	with open('database/challenges.pickle','rb') as file:
		x = pickle.load(file)
	return x
