from app import app, db, User, login_manager
# from classes import User # User
from utils import *
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from mylib.cipher import encode, decode
from mylib.mail import send_email_to_somebody
from constants import SECURITY_QUESTIONS, challenge_dict
from challenges import Entry, read_challenges, write_challenges
from pprint import pprint
import datetime, pickle
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user

# TODO
'''
normal leaderboard
cmd f read('users.txt') and remove them
completely delete user_mapping.txt and all references to it
fix get_user_id and get_username in utils to use database

long term
refactor other database items like challenges and challenge_suggestions
'''

COMMENT = ''
verbose = read('args.txt')['verbose']


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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# routes in the app
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
		users = User.query.all()
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
			signup1 = {
				'first_name':to_name_case(first_name),
				'last_name':to_name_case(last_name),
				'age':age,
				'gender':gender
			}
			users_lst = list(users)[:-1] # everything but last one
			for user in users_lst:
				if user.first_name == to_name_case(first_name) \
				and user.last_name == to_name_case(last_name):
					flash('You have already registered for an account')
					return render_template("unauth/signup.html")
			variables['half_user'] = signup1
			# variables['current_user_id'] = user.id
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
			users_lst = list(users)[:-1] # all but current one which is only partly signed up.
			for user in users_lst:
				if verbose:
					print(user)
					print('username: ',user.username)
					print(user.username == username)
				if user.username == username:
					flash('That username is already taken')
					return render_template("signup2.html", password=password, confirm_password=confirm_password, security_questions=SECURITY_QUESTIONS, security_question_id=security_question_id, answer=answer)

			variables = read('vars.txt')
			v = variables['half_user']
			id = len(User.query.all())
			print('user id is ',id)
			user = User(id=id,
						first_name=v['first_name'],
			 			last_name=v['last_name'],
			 			age=v['age'], 
			 			gender=v['gender'],
			 			username=username,
			 			password=encode(password),
			 			security_question_id=security['id'],
			 			security_question_ans=security['answer'])
			print('user: ',user)
			variables['half_user'] = None
			write('vars.txt', variables)

			challenges = read_challenges()
			challenges[user.id] = {}
			write_challenges(challenges)

			db.session.add(user)
			db.session.commit()
			return redirect('/'+username+'/')

	return render_template('unauth/signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		username = request.form.get('username')
		entered_password = request.form.get('password')
		try:
			user = User.query.filter_by(username=username).first()
		except KeyError:
			flash('Invalid Username')
			return render_template('unauth/login.html')
		password = decode(user.password)
		first_name = user.first_name
		if entered_password == password:
			# successful login
			# vars.txt is used to ensure the user did properly authenticate/sign up instead of using a url hack
			# remove this and use flask-login instead
			login_user(user)
			variables = read('vars.txt')
			# variables['logged_in'] = True
			write('vars.txt',variables)
			if verbose: print('you are logged in')
			return redirect('/'+ username)
		if entered_password != password and entered_password:
			flash('Incorrect Password')
			return render_template('unauth/login.html', username=username)
	return render_template('unauth/login.html')

@app.route('/forgot-password',methods=['GET','POST'])
def forgot_password():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		if username: # if there is no username in the form then they are on the next step. Ask them for security question
			# username step
			variables = read('vars.txt')
			variables['forgot_username'] = username
			write('vars.txt',variables)
			user = User.query.filter_by(username=username).first()
			if user is None:
				flash('That username does not exist')
				return redirect('/forgot-password')
			question_id = user.security_question_id
			question = id_to_question(question_id)
			return render_template('unauth/forgot_password.html', username=username, security_question=question)
		if not username and not password:
			# security question step
			variables = read('vars.txt')
			username = variables['forgot_username']
			user = User.query.filter_by(username=username).first()
			assert user is not None, f'could not find user with username {username}'
			entered_answer = request.form.get('answer')
			actual_answer = decode(user.security_question_ans)
			if entered_answer.lower() == actual_answer.lower(): # case insensitive
				if verbose: print('answers match!')
				return render_template('unauth/forgot_password.html',success=True)
			else:
				question_id = user.security_question_id
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
			if verbose: print('new password is ',password)
			user = User.query.filter_by(username=username).first()
			user.password = encode(password)
			db.session.add(user)
			db.session.commit()
			variables['forgot_username'] = None
			write('vars.txt',variables)
			return redirect('/'+username+'/')
		else:
			print('something went wrong')
	return render_template('unauth/forgot_password.html')

@app.route('/<username>/logout')
@login_required
def logout(username):
	logout_user()
	return redirect('/')

@app.route('/<username>/')
@login_required
def home(username):
	name = User.query.filter_by(username=username).first().first_name
	return render_template('user/home.html', username=username, name=name)

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
@login_required
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
					[get_full_name(user_id), entry.score, entry.comment, user_id]
				)
		# `data` is a list containing lists that have †he same five things
		'''
		[
			placement (1st 2nd 3rd),
			full name of user,
			score of challenge,
			comment about challenge,
			user id
		]
		'''

		if checked:
			bn = [
				'12 and under male',
				'12 and under female',
				'teen/adult male',
				'teen/adult female'
			]
			brackets = get_brackets(data, selected_challenge_type)
			return render_template('user/leaderboard_brackets.html', tables=brackets, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				username=username, brackets=brackets, bracket_names=bn)
		else:
			sorted_data = sort_data(data, selected_challenge_type)
			print('no brackets')
			return render_template('user/userleaderboard.html', data=sorted_data, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				username=username,checked=repr(checked))
	return render_template('user/userleaderboard.html',challenge_dict=challenge_dict,header="Leaderboard",username=username)


@app.route('/<username>/records-add',methods=['GET','POST'])
@login_required
def records_add(username):
	global COMMENT
	# entry(11.98,datetime.datetime.today(),'hand over hand')
	if request.method == "POST":
		challenge = request.form.get('challenge')
		challenge_type = get_challenge_type(challenge)
		score = request.form.get('time')
		comment = request.form.get('comment')
		COMMENT = comment
		if verbose:
			print(challenge_type)
		if challenge_type == 'time':
			try:
				score = float(score)
			except ValueError:
				flash('Please enter a number for score')
				return redirect('/'+username+'/records-add')
		if challenge_type in ['reps', 'laps']:
			try:
				score = int(score)
			except ValueError:
				flash('Please only enter a whole number for ' + challenge_type)
				return redirect('/'+username+'/records-add')
		date = datetime.datetime.today()
		en = Entry(score, date, comment)
		user_id = get_user_id(username)

		challenges = read_challenges()
		try:
			# there is already an entry for the challenge. append the entry to the list
			if verbose:
				print('adding challenge to dict for databse. Challenge is: '+ challenge) 
			challenges[user_id][challenge].append(en)
		except KeyError:
			# there is no entry for that challenge yet. Create a list for it and add the entry
			challenges[user_id][challenge] = [en]
		if verbose:
			print(COMMENT)
			print(en)
		write_challenges(challenges)
		COMMENT = ''
		return redirect('/'+username+'/records-view')
	if verbose:
		print('COMMENT: ',COMMENT)
	return render_template('user/personal_records_add.html',challenge_dict=challenge_dict,username=username,comment=COMMENT)

@app.route('/<username>/records-view')
@login_required
def records_view(username):
	user_id = get_user_id(username)
	challenges = read_challenges()
	ch = challenges[user_id]
	return render_template('user/personal_records_view.html',challenge_dict=challenge_dict,username=username, ch=ch)

@app.route('/<username>/suggest-challenge',methods=['GET','POST'])
@login_required
def suggest_challenge(username):
	if request.method == "POST":
		challenge_type = request.form.get('type')
		challenge_name = request.form.get('challenge')
		challenge_submission = {
			'type':challenge_type,
			'name':challenge_name,
			'username':username
		}
		user_id = get_user_id(username)
		name = User.query.filter_by(username=username).first().first_name
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
		return render_template('user/home.html', username=username, name=name)
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
# 