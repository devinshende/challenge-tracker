import os
from constants import SECURITY_QUESTIONS, challenge_dict
from challenges import Entry
import datetime

def json_to_objects(userchallenges):
	"turns lists of [score, datetime_obj, comment] into Entry objects with all those things"
	ch = {}
	for challenge_name, entries in userchallenges.items():
		ch[challenge_name] = []
		for jsonentry in entries:
			ch[challenge_name].append(Entry(jsonentry))
	return ch

def reset_user_challenges(username):
	"this should be used from a python console. clears all the user's challenges data"	
	from app import db, User
	user = User.query.filter_by(username=username).first()
	user.challenges = {}
	db.session.add(user)
	db.session.commit()

def datetime_to_string(date):
	"takes datetime object and turns it into a string like 'month.day.year' "
	# 8.24.2019
	try:
		return f'{date.month}.{date.day}.{date.year}'
	except:
		if type(date) == datetime.datetime:
			raise ValueError(f'input `{date}` is not a datetime object')
		raise ValueError(f'bad input: `{date}`')

# def get_empty_challenges_dict():
# 	chs = {}
# 	for lst in challenge_dict.values():
# 		for i in lst:
# 			chs[i] = []
# 	return chs

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
	files = ['args','challenge_suggestions','users','vars']
	for f in files:
		write(f+'.txt','')
	write('args.txt',{'email':False,'verbose':False})

def get_user_id(username):
	"gets user id from username"
	from app import User
	return User.query.filter_by(username=username).first().id

def get_username(user_id):
	"gets username from a user's id "
	from app import User
	return User.query.get(user_id).username

def get_full_name(user_id):
	"gets full name (first and last) of a user from their `user_id`"
	from app import User
	user = User.query.get(user_id)
	assert user is not None, f'there is no user for the user_id {user_id}'
	print(user)
	return user.first_name + ' ' + user.last_name

def question_to_id(question):
	"takes a security question and returns its id"
	if question not in SECURITY_QUESTIONS:
		print(f'{question} not in SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS.index(question)

def id_to_question(ID):
	"takes a security question id and returns its string"
	if ID > len(SECURITY_QUESTIONS):
		print(f'{ID} is too big to be one of the accepted SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS[ID]

def get_best(entry_list,ch_type):
	"gets the best entry (scorewise based on `ch_type`) out of an `entry_list`"
	if not entry_list:
		return None
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
	"returns type of challenge that the string `challenge` is"
	for ch_type,lst in challenge_dict.items():
		if challenge in lst:
			return ch_type
	raise ValueError('that challenge `'+challenge+'` is not in challenge_dict')

def get_brackets(data, selected_challenge_type):
	"takes in `data` then sorts it based on the `selected_challenge_type` and splits it up into brackets"
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
		if age < 13: #in kid's division
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
	"takes in `sorted_data` and returns modified `sorted_data` to have places for each competitor"
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
