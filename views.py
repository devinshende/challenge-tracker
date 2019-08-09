from app import app
from utils import *
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from mylib.cipher import encode, decode
from mylib.mail import send_email_to_somebody
from constants import SECURITY_QUESTIONS, challenge_dict
from challenges import Entry, read_challenges, write_challenges
from pprint import pprint
import datetime, pickle

COMMENT = ''
verbose = read('args.txt')['verbose']
# user_so_far = None

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return "500 error"+str(error)

@app.route('/')
def landing_page():
	variables = read('vars.txt')
	for key, _ in variables.items():
		variables[key] = None
	variables['logged_in'] = False # everything but this should be set to False
	write('vars.txt',variables)
	return render_template('unauth/landing_page.html') # kwargs are used for html

@app.route('/api/<filename>')
def api(filename):
	if filename != 'challenges.pickle':
		with open('database/'+filename,'r') as file:
			data = file.read()
	else:
		data = read_challenges()
	return str(data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	# global user_so_far
	if request.method == 'POST':
		users = read('users.txt')
		variables = read('vars.txt')
		first_name = request.form.get('first_name')
		if first_name:
			# signup1
			if verbose:
				print('in signup 1')
			first_name = request.form.get('first_name')
			last_name = request.form.get('last_name')
			age = request.form.get('age')
			gender = request.form.get('gender')
			user_id = len(users)
			signup1 = {
				'user_id':user_id,
				'first_name':to_name_case(first_name),
				'last_name':to_name_case(last_name),
				'age':age,
				'gender':gender
			}
			users_lst = list(users.values())[:-1] # everything but last one
			for user in users_lst:
				if user["first_name"] == to_name_case(first_name) \
				and user["last_name"] == to_name_case(last_name):
					flash('You have already registered for an account')
					return render_template("signup.html")
			variables['half_user'] = signup1
			variables['current_user_id'] = user_id
			write('vars.txt',variables)
			return render_template('unauth/signup2.html', security_questions=SECURITY_QUESTIONS)
		else:
			# signup2
			if verbose:
				print('in signup2')
			# switching over to signup2 template
			username = request.form.get('username')
			password = request.form.get('password')
			confirm_password = request.form.get('confirm_password')
			security_question = request.form.get('security_question')
			security_question_id = question_to_id(security_question) # convert string of question to it's id in SECURITY_QUESTIONS
			answer = request.form.get('answer')
			security = {'id':security_question_id,'answer':encode(answer)}
			users_lst = list(users.values())[:-1] # all but current one which is only partly signed up.
			for user in users_lst:
				if verbose:
					print(user)
					print('username: ',user['username'])
					print(user['username'] == username)
				if user["username"] == username:
					flash('That username is already taken')
					return render_template("signup2.html", password=password, confirm_password=confirm_password, security_questions=SECURITY_QUESTIONS, security_question_id=security_question_id, answer=answer)

			# print(user_id)
			variables = read('vars.txt')
			user = variables['half_user']
			user_id = user['user_id']
			user['username'] = username
			user['password'] = encode(password)
			user['security_question'] = security
			users[user_id] = user
			write('users.txt', users)
			variables['half_user'] = None
			write('vars.txt', variables)
			user_mapping = read('user_mapping.txt')
			user_mapping[username] = user_id
			write('user_mapping.txt',user_mapping)

			challenges = read_challenges()
			challenges[user_id] = {}
			write_challenges(challenges)
			return redirect('/'+username+'/')

	return render_template('unauth/signup.html')


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
			return render_template('unauth/login.html')
		password = decode(users[user_id]['password'])
		user_id = user_mapping[username]
		first_name = users[user_id]['first_name']
		if entered_password == password:
			# successful login
			# vars.txt is used to ensure the user did properly authenticate/sign up instead of using a url hack
			variables = read('vars.txt')
			variables['logged_in'] = True
			write('vars.txt',variables)
			if verbose: print('you are logged in')
			return redirect('/'+ username)
		if entered_password != password and entered_password:
			flash('Incorrect Password')
			return render_template('unauth/login.html', username=username)
	return render_template('unauth/login.html')

@app.route('/forgot-password',methods=['GET','POST'])
def forgot_password():
	users = read('users.txt')
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		if username: # if there is no username in the form then they are on the next step. Ask them for security question
			# username step
			variables = read('vars.txt')
			variables['forgot_username'] = username
			write('vars.txt',variables)
			try:
				user_id = get_user_id(username)
			except KeyError:
				flash('That username does not exist')
				return redirect('/forgot-password')
			question_id = users[user_id]['security_question']['id']
			question = id_to_question(question_id)
			return render_template('unauth/forgot_password.html', username=username, security_question=question)
		if not username and not password:
			# security question step
			variables = read('vars.txt')
			username = variables['forgot_username']
			user_id = get_user_id(username)
			entered_answer = request.form.get('answer')
			actual_answer = decode(users[user_id]['security_question']['answer'])
			if entered_answer.lower() == actual_answer.lower(): # case insensitive
				if verbose: print('answers match!')
				return render_template('unauth/forgot_password.html',success=True)
			else:
				question_id = users[user_id]['security_question']['id']
				question = id_to_question(question_id)
				if verbose: 
					print('answers do not match')
					print('question is ',question)
				flash('Incorrect Answer')
				return render_template('unauth/forgot_password.html', username=username, security_question=question)
		if password:
			# password step
			variables = read('vars.txt')
			username = variables['forgot_username']
			user_id = get_user_id(username)
			if verbose: print('new password is ',password)
			users[user_id]['password'] = encode(password)
			variables['forgot_username'] = None
			write('vars.txt',variables)
			write('users.txt',users)
			return redirect('/'+username+'/')
		else:
			print('something went wrong')
	return render_template('unauth/forgot_password.html')

@app.route('/<username>/')
def home(username):
	users = read('users.txt')
	user_mapping = read('user_mapping.txt')
	user_id = user_mapping[username]
	name = users[user_id]['first_name']
	return render_template('user/home.html', username=username, users=users, name=name)

@app.route('/leaderboard',methods=['GET','POST'])
def leaderboard():
	if request.method == "POST":
		selected_challenge = request.form.get('challenge')
		selected_challenge_type = get_challenge_type(selected_challenge)
		challenges = read_challenges()
		data = []
		for user_id,usr_challenges_dict in challenges.items():
			if selected_challenge in usr_challenges_dict.keys():
				entry = get_best(usr_challenges_dict[selected_challenge], selected_challenge_type)
				data.append(
					(get_full_name(user_id), entry.score, entry.format_date(), entry.comment)
				)
		# `data` is a list containing tuples that have †he same four things
		'''
		(
			full name of user,
			score of challenge,
			date of doing challenge,
			comment about challenge
		)
		'''
		if selected_challenge_type in ['reps','laps']:
			# sort it so highest score is first in `data`
			# sort it lowest first then reverse list
			sorted_data = sorted(data, key=lambda x:x[1])[::-1]
		elif selected_challenge_type  == 'time':
			# sort so lowest score is first in the `data`
			sorted_data = sorted(data, key=lambda x:x[1])
		return render_template('unauth/leaderboard.html', data=sorted_data, header=selected_challenge, \
			challenge_type=to_name_case(selected_challenge_type) \
			)
	return render_template('unauth/leaderboard.html',challenge_dict=challenge_dict,header="Leaderboard")

@app.route('/<username>/leaderboard',methods=['GET','POST'])
def userleaderboard(username):
	if request.method == "POST":
		selected_challenge = request.form.get('challenge')
		checked = request.form.get('bracketswitch')
		selected_challenge_type = get_challenge_type(selected_challenge)
		challenges = read_challenges()
		data = []
		for user_id,usr_challenges_dict in challenges.items():
			if selected_challenge in usr_challenges_dict.keys():
				entry = get_best(usr_challenges_dict[selected_challenge], selected_challenge_type)
				data.append(
					(get_full_name(user_id), entry.score, entry.format_date(), entry.comment)
				)
		# `data` is a list containing tuples that have †he same four things
		'''
		(
			full name of user,
			score of challenge,
			date of doing challenge,
			comment about challenge
		)
		'''
		if selected_challenge_type in ['reps','laps']:
			# sort it so highest score is first in `data`
			# sort it lowest first then reverse list
			sorted_data = sorted(data, key=lambda x:x[1])[::-1]
		elif selected_challenge_type  == 'time':
			# sort so lowest score is first in the `data`
			sorted_data = sorted(data, key=lambda x:x[1])
		return render_template('user/userleaderboard.html', data=sorted_data, header=selected_challenge, \
			challenge_type=to_name_case(selected_challenge_type), \
			username=username,checked=repr(checked))
	return render_template('user/userleaderboard.html',challenge_dict=challenge_dict,header="Leaderboard",username=username)


@app.route('/<username>/records-add',methods=['GET','POST'])
def records_add(username):
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
			return redirect('/'+username+'/records-add')
		date = datetime.datetime.today()
		en = Entry(time, date, comment)
		user_mapping = read('user_mapping.txt')
		user_id = user_mapping[username]

		challenges = read_challenges()
		try:
			# there is already an entry for the challenge. append the entry to the list
			if verbose:
				print('adding challenge to dict for databse')
			challenges[user_id][challenge].append(en)
		except KeyError:
			# there is no entry for that challenge yet. Create a list for it and add the entry
			challenges[user_id][challenge] = [en]
		if verbose:
			print(COMMENT)
		write_challenges(challenges)
		COMMENT = ''
		return redirect('/'+username+'/records-view')
	if verbose:
		print('COMMENT: ',COMMENT)
	return render_template('user/personal_records_add.html',challenge_dict=challenge_dict,username=username,comment=COMMENT)

@app.route('/<username>/records-view')
def records_view(username):
	user_mapping = read('user_mapping.txt')
	user_id = user_mapping[username]
	challenges = read_challenges()
	print(verbose)
	if verbose: 
		print(type(challenges))
		print(challenges)
		print('user id',user_id)
		print(challenges[user_id])
	ch = challenges[user_id]
	return render_template('user/personal_records_view.html',challenge_dict=challenge_dict,username=username, ch=ch)

@app.route('/<username>/suggest-challenge',methods=['GET','POST'])
def suggest_challenge(username):
	if request.method == "POST":
		challenge_type = request.form.get('type')
		challenge_name = request.form.get('challenge')
		challenge_submission = {
			'type':challenge_type,
			'name':challenge_name,
			'username':username
		}
		users = read('users.txt')
		user_mapping = read('user_mapping.txt')
		user_id = user_mapping[username]
		name = users[user_id]['first_name']
		send_emails = read('args.txt')['email']
		if verbose: print('writing suggestion to database')
		# save suggestion to database
		suggestions = read('challenge_suggestions.txt','list')
		suggestions.append(challenge_submission)
		write('challenge_suggestions.txt',suggestions)
		if send_emails == True:
			send_email_to_somebody('Challenge submission',repr(challenge_submission),'devin.s.shende@gmail.com')
			send_email_to_somebody('Challenge submission',repr(challenge_submission),'ravi.sameer.shende@gmail.com')
		else:
			if verbose:
				print('would be sending emails but that was set to False so not doing that.')
		return render_template('user/home.html', username=username, users=users, name=name)
	return render_template('user/new_challenge.html',username=username)

@app.route('/admin')
def admin_login():
	if verbose: print('Admin home page')
	return render_template('admin/admin_home.html',username='stillworkingonusername')

@app.route('/admin/suggestions')
def admin_suggestions():
	if verbose: print('Admin see suggestions page')
	suggestions=read('challenge_suggestions.txt')
	return render_template('admin/admin_suggestions.html',json=suggestions,username='stillworkingonusername')

@app.route('/table')
def table():
	return render_template('unauth/my_table.html')
