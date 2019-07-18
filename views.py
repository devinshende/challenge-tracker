from app import app, read, write

from flask import Flask, render_template, request, redirect, url_for, flash
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, question_to_id, id_to_question
from challenges import Entry, challenges, challenge_list
from pprint import pprint
import datetime
COMMENT = ''

@app.route('/')
def landing_page():
	print(app)
	return render_template('landing_page.jinja2') # kwargs are used for jinja2

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
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
		challenges[user_id] = {}
		print('new user added')
		print(username)
		# pprint(users)
		# pprint(user_mapping)
		return redirect('/')
	return render_template('signup2.jinja2', security_questions = SECURITY_QUESTIONS)


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
		password = decode(users[user_id]['password'])
		user_id = user_mapping[username]
		first_name = users[user_id]['first_name']
		if entered_password == password:
			return redirect('/'+username)
		if entered_password != password and entered_password:
			flash('Invalid Password')
			return render_template('login.jinja2', username=username)
	return render_template('login.jinja2')

@app.route('/<username>/')
def home(username):
	users = read('users.txt')
	user_mapping = read('user_mapping.txt')
	user_id = user_mapping[username]
	name = users[user_id]['first_name']
	return render_template('home.jinja2', username=username, users=users, name=name)

@app.route('/leaderboard')
def leaderboard():
	return 'Riley Cvitanich wins'

@app.route('/<username>/records',methods=['GET','POST'])
def records(username):
	global COMMENT
	# entry(11.98,datetime.datetime.today(),'hand over hand')
	if request.method == "POST":
		challenge = request.form.get('challenge')
		time = request.form.get('time')
		comment = request.form.get('comment')
		COMMENT = comment
		try:
			time = float(time)
		except ValueError:
			flash('please enter a number for score')
			return redirect('/'+username+'/records')
		date = datetime.datetime.today()
		en = Entry(time, date, comment)
		user_mapping = read('user_mapping.txt')
		user_id = user_mapping[username]
		try:
			# there is already an entry for the challenge. append the entry to the list
			challenges[user_id][challenge].append(en)
		except KeyError:
			# there is no entry for that challenge yet. Create a list for it and add the entry
			challenges[user_id][challenge] = [en]
		# pprint(challenges)
		print(COMMENT)
		COMMENT = ''
		print()
		return render_template('personal_records.jinja2', 
			challenge_list=challenge_list,
			ch=challenges[user_id],
			username=username,
			comment=COMMENT)
	print('COMMENT: ',COMMENT)
	return render_template('personal_records.jinja2',challenge_list=challenge_list,username=username,comment=COMMENT)






