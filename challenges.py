
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
		date = self.date.strftime("%A, %B %dth, %Y")
		return f'Entry(score:{self.score} date:{date} comment: {self.comment})'


challenge_list = [
	'Devil Steps - Speed',
	'Rings - Laps',
	'Warped Wall - repetitions in 1 minute',
	'Campus Board hopping - speed',
	'Floating Steps - laps in one minute',
	'Campus Board - Laps',
]

challenges = {
	0:{},
	1:{},
	2:{},
	3:{},
	4:{}
}