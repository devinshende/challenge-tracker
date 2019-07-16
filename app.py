from flask import Flask, render_template, request, redirect, url_for, flash
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, question_to_id, id_to_question
from challenges import entry, challenges, challenge_list
from pprint import pprint
import datetime
import ast
import os
import datetime

#UNFINISHED BUSINESS FOR SIGNUPS
'''
feedback to show that user was successfully added
styles to make it look not awful
'''

def read(file_name):
	with open(os.path.join('database',file_name), 'r') as file:
		x = file.read()
	try:
		return eval(x)
	except SyntaxError:
		return {}

def write(file_name, data):
	with open(os.path.join('database',file_name), 'w') as file:
		file.write(str(data))

app = Flask(__name__)
app.static_folder = 'static'

app.secret_key = 'jsahgfdjshgfsdjgghayfdsajhsfdayda'

@app.route('/')
def landing_page():
	return render_template('landing_page.jinja2') # kwargs are used for jinja2

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		first_name = request.form.get('firstName')
		last_name = request.form.get('lastName')
		age = request.form.get('age')
		gender = request.form.get('gender')
		users = read('users.txt')
		user_id = len(users)
		
		users[user_id] = {
			'user_id':user_id,
			'first_name':first_name,
			'last_name':last_name,
			'age':age,
			'gender':gender
		}
		
		write('users.txt', users)

		return redirect('/signup/2')
	return render_template('signup.jinja2')


@app.route('/signup/2', methods=['GET','POST'])
def signup2():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		security_question = request.form.get('security_question')
		security_question_id = question_to_id(security_question) # convert string of question to it's id in SECURITY_QUESTIONS
		answer = request.form.get('answer')
		security = {'id':security_question_id,'answer':encode(answer)}

		users = read('users.txt')
		user_id = len(users) - 1
		users[user_id]['username'] = username
		users[user_id]['password'] = encode(password)
		users[user_id]['security_question'] = security
		
		write('users.txt', users)
		user_mapping = read('user_mapping.txt')
		user_mapping[username] = user_id
		write('user_mapping.txt',user_mapping)
		# pprint(users)
		# pprint(user_mapping)
		return redirect('/')
	return render_template('signup2.jinja2', security_questions = SECURITY_QUESTIONS)

USER = 0
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		username = request.form.get('username')
		entered_password = request.form.get('password')
		user_mapping = read('user_mapping.txt')
		users = read('users.txt')
		try:
			user_id = user_mapping[username]
		except KeyError:
			flash('Invalid Username')
			return render_template('login.jinja2')
		USER = user_id
		password = decode(users[user_id]['password'])

		
		if entered_password == password:
			return redirect('/home')
		if entered_password != password and entered_password:
			flash('Invalid Password')
			return render_template('login.jinja2',username=username)
		
		# return f'welcome, {users[user_id]['first_name']}'

	return render_template('login.jinja2')

@app.route('/home')
def home():
	user_id = USER
	users = read('users.txt')
	return render_template('home.jinja2', user=users[user_id])

@app.route('/leaderboard')
def leaderboard():
	return 'Riley Cvitanich wins'

@app.route('/records',methods=['GET','POST'])
def records():
	# entry(11.98,datetime.datetime.today(),'hand over hand')
	if request.method == "POST":
		challenge = request.form.get('challenges')
		time = float(request.form.get('time'))
		date = datetime.datetime.today()
		comment = request.form.get('comment')
		en = entry(time, date, comment)
		print(challenge)
		return render_template('personal_records.jinja2',entry=en,challenges=challenge_list)
	return render_template('personal_records.jinja2',challenges=challenge_list)

app.run()
