from mylib.cipher import decode
import json


PROF_PICS_PATH = 'static/profile_pics'

'''
DO NOT DELETE
SECURITY_QUESTIONS = [
	"What was the name of your first pet?",
	"What is your favorite number?",
	"How old were you when you first got the warped wall?",
	"What school did you attend in kindergarten?"
]

challenge_dict = {
	"time":[
		"Devil Steps",
		"Campus Board (up and down)",
		"Floating Doors to Cliffhanger",
		"Rope Climb"
	],

	"laps":[
		"Rings",
		"Campus Board",
		"Balance Beam Slack Line"
	],

	"reps":[
		"Warped Wall",
		"Quintuple Steps"
	]
}
'''

def load_challenge_dict():
	with open('database/challenges.json','r') as file:
		json_str = file.read()
		challenge_dict = json.loads(json_str)
	return challenge_dict

def load_security_questions():
	with open('database/security_questions.json','r') as file:
		json_str = file.read()
		SECURITY_QUESTIONS = json.loads(json_str)['list']
	return SECURITY_QUESTIONS

BRACKETS = [
	'12 and under boys',
	'12 and under girls',
	'teen/adult boys',
	'teen/adult girls'
]

monthsDict = {
	'January':1, 'February':2, 'March':3,
	'April':4, 'May':5, 'June':6, 
	'July':7, 'August':8, 'September':9, 
	'October':10, 'November':11, 'December':12
}

class Password(object):
	def __init__(self, password):
		self.decoded = decode(password)
		self.encoded = password

ADMIN_PASSWORD = Password('+5PmZmMJFJ499')

SECURITY_QUESTIONS = load_security_questions()

TC_COLORS = [
	"grey",
	"red",
	"green",
	"yellow",
	"blue",
	"magenta",
	"cyan",
	"white"
]

