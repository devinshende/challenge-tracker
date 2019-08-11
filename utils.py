import os
from constants import SECURITY_QUESTIONS, challenge_dict

def to_name_case(name):
	"converts name to have first letter uppercase and the rest lowercase"
	if not name:
		raise ValueError('you must enter a string for the name. '+str(name)+' is not a valid string')
	first_letter = name[0]
	rest_of_name = name[1:]
	return first_letter.upper() + rest_of_name.lower()

def read(file_name,type='dict'):
	"returns data from `file_name` in the database"
	with open(os.path.join('database',file_name), 'r') as file:
		x = file.read()
	try:
		return eval(x) # gets dictionary of string
	except:
		if type=='dict':
			return {}
		if type=='list':
			return []

def write(file_name, data):
	"writes `data` to `file_name` in database"
	with open(os.path.join('database',file_name), 'w') as file:
		file.write(str(data))

def reset_all():
	"clears all data from all database files"
	raise SyntaxError('fix reset all to work with challenges.pickle and database before running this')
	files = ['args','challenge_suggestions','user_mapping','users','vars']
	for f in files:
		write(f+'.txt','')
	write('args.txt',{'email':False,'verbose':False})

def get_user_id(username):
	from app import User
	return User.query.filter_by(username=username).first().id

def get_username(user_id):
	from app import User
	return User.query.get(user_id).username

def get_full_name(user_id):
	from app import User
	user = User.query.get(user_id)
	assert user is not None, f'there is no user for the user_id {user_id}'
	print(user)
	return user.first_name + ' ' + user.last_name

def question_to_id(question):
	if question not in SECURITY_QUESTIONS:
		print(f'{question} not in SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS.index(question)

def id_to_question(ID):
	if ID > len(SECURITY_QUESTIONS):
		print(f'{ID} is too big to be one of the accepted SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS[ID]

def get_best(entry_list,ch_type):
	best_so_far = entry_list[0]
	for entry in entry_list:
		if ch_type == 'reps' or ch_type == 'laps':
			if entry.score > best_so_far.score:
				best_so_far = entry
		elif ch_type == 'time':
			if entry.score < best_so_far.score:
				best_so_far = entry
	return best_so_far

def get_challenge_type(challenge):
	for ch_type,lst in challenge_dict.items():
		if challenge in lst:
			return ch_type
	else:
		raise ValueError('that challenge ('+challenge+') is not in challenge_dict')

def get_brackets(data, selected_challenge_type):
	from app import User
	# `data` is a list containing lists that have †he same four things
	'''
	[
		placement (1st 2nd 3rd)
		full name of user,
		score of challenge,
		comment about challenge,
		user id
	]
	'''
	mkid = []
	fkid = []
	madult = []
	fadult = []

	for person in data:
		user_id = person[-1]
		age = int(User.query.get(user_id).age)
		gender = User.query.get(user_id).gender
		if age < 13: #in kid's divisino
			if gender == 'male':
				mkid.append(person)
			else:
				fkid.append(person)
		else: #in adult's division
			if gender == 'male':
				madult.append(person)
			else:
				fadult.append(person)
		# get_username()	
	brackets = (mkid, fkid, madult, fadult)
	result = []
	for bracket in brackets:
		 result.append(
		 	sort_data(bracket, selected_challenge_type)
		 	)
	return result

def sort_data(data, selected_challenge_type):
	"sorts data and then adds placements"
	#sorts data based on score
	if selected_challenge_type in ['reps','laps']:
		# sort it so highest score is first in `data`
		# sort it lowest first then reverse list
		sorted_data = sorted(data, key=lambda x:x[1])[::-1]
	elif selected_challenge_type  == 'time':
		# sort so lowest score is first in the `data`
		sorted_data = sorted(data, key=lambda x:x[1])
	return add_places(sorted_data)
	
	# `sorted_data` is a sorted list containing lists that have †he same 5 things
	'''
	[
		placement -- to be inserted here
		full name of user,
		score of challenge,
		comment about challenge,
		user id
	]
	'''
	# x.insert(index, item)
	#adds placements and deals with ties


def add_places(sorted_data):
	if not sorted_data:
		return None
	prev_score = sorted_data[0][1]
	prev_place = 1
	print(sorted_data[0])
	sorted_data[0].insert(0, prev_place)
	for item in sorted_data[1:]:
		print(f'\nprev_place is {prev_place}')
		print(f'\tprev_score: {prev_score}\n\tcurrent score: {item[1]}')
		if prev_score == item[1]:
			print(f'scores match. setting place for {item[0]} to {prev_place}')
			place = prev_place
		else:
			print(f'scores do not match. setting place for {item[0]} to {prev_place+1}')
			place = prev_place + 1
		sorted_data[sorted_data.index(item)].insert(0, place)
		prev_score = item[2] # 2 for score because new item was inserted
		prev_place = place

	final_data = sorted_data
	print(final_data)
	return final_data
