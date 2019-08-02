from app import app, read, write
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from mylib.cipher import encode, decode
from mylib.mail import send_email_to_somebody
from constants import SECURITY_QUESTIONS, question_to_id, id_to_question
from challenges import Entry, challenges, challenge_dict
from pprint import pprint
import datetime

COMMENT = ''
verbose = read('args.txt')['verbose']

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.jinja2'), 404


@app.errorhandler(500)
def internal_error(error):
    return "500 error"+str(error)

@app.route('/')
def landing_page():
	variables = read('vars.txt')
	variables['current_user_id'] = None
	variables['logged_in'] = False
	write('vars.txt',variables)
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
		variables = read('vars.txt')
		variables['current_user_id'] = user_id
		write('vars.txt',variables)
		if verbose:
			print('current_user_id ',user_id)
			print('user so far')
			pprint(users[user_id])
		write('users.txt', users)

		return redirect('/signup2')
	return render_template('signup.jinja2')

@app.route('/signup2', methods=['GET','POST'])
def signup2():
	users = read('users.txt')
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		security_question = request.form.get('security_question')
		security_question_id = question_to_id(security_question) # convert string of question to it's id in SECURITY_QUESTIONS
		answer = request.form.get('answer')
		security = {'id':security_question_id,'answer':encode(answer)}

		user_id = len(users) - 1
		users[user_id]['username'] = username
		users[user_id]['password'] = encode(password)
		users[user_id]['security_question'] = security
		
		write('users.txt', users)
		user_mapping = read('user_mapping.txt')
		user_mapping[username] = user_id
		write('user_mapping.txt',user_mapping)
		challenges[user_id] = {}
		if verbose:
			print('new user added')
			print(username)
		# vars.txt is used to ensure the user did properly authenticate/sign up instead of using a url hack
		variables = read('vars.txt')
		variables['current_user_id'] = user_id
		variables['logged_in'] = True
		write('vars.txt',variables)
		return redirect('/'+ username)

	try:
		user_id = read('vars.txt')['current_user_id']
		if verbose: print('your user id is ',user_id)
		first_name_test = users[user_id]['first_name']
		if verbose: print('first name is',first_name_test,'Rendering signup2')
	except KeyError:
		print('first name doesn\'t exist. Redirecting you to signup1')
		return redirect('/signup')
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
			# successful login
			# vars.txt is used to ensure the user did properly authenticate/sign up instead of using a url hack
			variables = read('vars.txt')
			variables['logged_in'] = True
			write('vars.txt',variables)
			if verbose: print('you are logged in')
			return redirect('/'+ username)
		if entered_password != password and entered_password:
			flash('Incorrect Password')
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
	return render_template('leaderboard.jinja2')

@app.route('/<username>/leaderboard')
def userleaderboard(username):
	return render_template('userleaderboard.jinja2',username=username)

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
			if verbose:
				print('adding challenge to dict for databse')
				print('challenges:')
				pprint(challenges)
			challenges[user_id][challenge].append(en)
		except KeyError:
			# there is no entry for that challenge yet. Create a list for it and add the entry
			challenges[user_id][challenge] = [en]
		if verbose:
			pprint(challenges)
			print(COMMENT)
		COMMENT = ''
		return render_template('personal_records.jinja2', 
			challenge_dict=challenge_dict,
			ch=challenges[user_id],
			username=username,
			comment=COMMENT)
	if verbose:
		print('COMMENT: ',COMMENT)
	return render_template('personal_records.jinja2',challenge_dict=challenge_dict,username=username,comment=COMMENT)

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
		return render_template('home.jinja2', username=username, users=users, name=name)
	return render_template('new_challenge.jinja2',username=username)

@app.route('/admin')
def admin_login():
	if verbose: print('Admin home page')
	return render_template('admin_home.jinja2',username='stillworkingonusername')

@app.route('/admin/suggestions')
def admin_suggestions():
	if verbose: print('Admin see suggestions page')
	suggestions=read('challenge_suggestions.txt')
	return render_template('admin_suggestions.jinja2',json=suggestions,username='stillworkingonusername')

