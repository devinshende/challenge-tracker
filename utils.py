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
	raise SyntaxError('fix reset all to work with challenges.pickle before running this')
	files = ['args','challenge_suggestions','user_mapping','users','vars']
	for f in files:
		write(f+'.txt','')
	write('args.txt',{'email':False,'verbose':False})

def get_user_id(username):
	user_mapping = read('user_mapping.txt')
	return user_mapping[username]

def get_username(user_id):
	users = read('users.txt')
	return users[user_id]['username']

def get_full_name(user_id):
	users = read('users.txt')
	return users[user_id]['first_name'] + ' ' + users[user_id]['last_name']

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

def get_brackets(data):
	# `data` is a list containing tuples that have †he same four things
	'''
	(
		full name of user,
		score of challenge,
		date of doing challenge,
		comment about challenge,
		user id
	)
	'''
	users = read('users.txt')
	mkid = []
	fkid = []
	madult = []
	fadult = []

	for person in data:
		user_id = person[-1]
		age = int(users[user_id]['age'])
		gender = users[user_id]['gender']
		#in one of the kid divisions
		if age < 13: #is kid
			if gender == 'male': #is kid male
				mkid.append(person)
			else: #is kid female
				fkid.append(person)
		else: #is adult
			if gender == 'male': #is adult male
				madult.append(person)
			else: #is adult female
				print(f'appending \n{person}\nto adult female')
				fadult.append(person)
		# get_username()	
	print(f'returning \n{repr((mkid, fkid, madult, fadult))}\n')
	return (mkid, fkid, madult, fadult)







