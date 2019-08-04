import os
from constants import SECURITY_QUESTIONS

def to_name_case(name):
	"converts name to have first letter uppercase and the rest lowercase"
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

def question_to_id(question):
	if question not in SECURITY_QUESTIONS:
		print(f'{question} not in SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS.index(question)

def id_to_question(ID):
	if ID > len(SECURITY_QUESTIONS):
		print(f'{ID} is too big to be one of the accepted SECURITY_QUESTIONS')
	return SECURITY_QUESTIONS[ID]
