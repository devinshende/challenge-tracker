from app import *
from utils import *
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from mylib.cipher import encode, decode
from mylib.mail import send_email_to_somebody
from constants import SECURITY_QUESTIONS, challenge_dict, BRACKETS, PROF_PICS_PATH, monthsDict
from challenges import Entry
from pprint import pprint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user

try:
	verbose = read('args.txt')['verbose']
except KeyError:
	verbose = False


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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	# global user_so_far
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
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
			# age = request.form.get('age')
			yr = request.form.get('year')
			month = request.form.get('month')
			day = request.form.get('day')
			gender = request.form.get('gender')
			signup1 = {
				'first_name':to_name_case(first_name),
				'last_name':to_name_case(last_name),
				# 'age':age,
				'gender':gender,
				'year':yr,
				'month':month,
				'day':day
			}
			users_lst = list(users)[:-1] # everything but last one
			for user in users_lst:
				if user.first_name == to_name_case(first_name) \
				and user.last_name == to_name_case(last_name):
					flash('You have already registered for an account')
					return render_template("unauth/signup.html", months=months)
			print(month,day,yr)
			if month == 'month' or day == 'day' or yr == 'year':
				flash('Please fill out birthday')
				return render_template("unauth/signup.html", first_name=first_name, last_name=last_name, gender=gender, months=months, month=month, day=day, year=yr)
			variables['half_user'] = signup1
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
			id = User.query.all()[-1].id+1
			print('user id is ',id)
			month = int(monthsDict[v['month']])
			print(type(month))
			birthday = datetime(year=int(v['year']), month=month, day=int(v['day']))
			age = datetime.today().year - birthday.year
			print(type(birthday))
			user = User(id=id,
						first_name=v['first_name'],
			 			last_name=v['last_name'],
			 			age=age,
			 			birthday=birthday, #(db.Datetime) 
			 			gender=v['gender'],
			 			username=username,
			 			password=encode(password),
			 			security_question_id=security['id'],
			 			security_question_ans=security['answer'])
			print('user: ',user)
			variables['half_user'] = None
			write('vars.txt', variables)

			db.session.add(user)
			db.session.commit()
			user = User.query.get(id)
			if user is not None:
				login_user(user)
			return redirect('/'+username+'/')
	return render_template('unauth/signup.html', months=months)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		username = request.form.get('username')
		entered_password = request.form.get('password')
		user = User.query.filter_by(username=username).first()
		if user is None:
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
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	name = user.first_name
	return render_template('user/home.html', username=username, user=user)

@app.route('/leaderboard',methods=['GET','POST'])
def leaderboard():
	all_users = User.query.all()
	if request.method == "POST":
		selected_challenge = request.form.get('challenge')
		checked = request.form.get('bracketswitch')
		selected_challenge_type = get_challenge_type(selected_challenge)
		data = []
		for user in all_users:
			user_challenges = json_to_objects(user.challenges)
			if selected_challenge in user_challenges.keys():
				entry = get_best(user_challenges[selected_challenge], selected_challenge_type)
				data.append(
					[user.get_profile_pic(),
					get_full_name(user.id),
					entry.score,
					entry.comment,
					user.id]
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
			return render_template('unauth/leaderboard_brackets.html', tables=brackets, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				brackets=brackets, bracket_names=bn)
		else:
			sorted_data = sort_data(data, selected_challenge_type)
			print('no brackets')
			return render_template('unauth/leaderboard_no_brackets.html', data=sorted_data, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				checked=repr(checked))
	return render_template('unauth/leaderboard_no_brackets.html',challenge_dict=challenge_dict,header="Leaderboard")

@app.route('/<username>/leaderboard',methods=['GET','POST'])
@login_required
def userleaderboard(username):
	user = User.query.filter_by(username=username).first()
	all_users = User.query.all()
	if request.method == "POST":
		selected_challenge = request.form.get('challenge')
		checked = request.form.get('bracketswitch')
		selected_challenge_type = get_challenge_type(selected_challenge)
		data = []
		for user in all_users:
			user_challenges = json_to_objects(user.challenges)
			if selected_challenge in user_challenges.keys():
				entry = get_best(user_challenges[selected_challenge], selected_challenge_type)
				data.append(
					[user.get_profile_pic(),
					get_full_name(user.id),
					entry.score,
					entry.comment,
					user.id]
				)
		# `data` is a list containing lists that have †he same five things
		'''
		[
			placement (1st 2nd 3rd),
			full name of user,
			user's profile picture,
			score of challenge,
			comment about challenge,
			user id
		]
		'''

		if checked:
			brackets = get_brackets(data, selected_challenge_type)
			return render_template('user/leaderboard_brackets.html', tables=brackets, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				username=username, brackets=brackets, bracket_names=BRACKETS, user=user)
		else:
			sorted_data = sort_data(data, selected_challenge_type)
			print('no brackets')
			return render_template('user/leaderboard_no_brackets.html', data=sorted_data, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				username=username,checked=repr(checked), user=user)
	return render_template('user/leaderboard_no_brackets.html',challenge_dict=challenge_dict, header="Leaderboard", \
		username=username, user=user)


@app.route('/<username>/records-add',methods=['GET','POST'])
@login_required
def records_add(username):
	user = User.query.filter_by(username=username).first()
	# user = db.session.query(User).filter_by(username=username).first()
	if request.method == "POST":
		challenge = request.form.get('challenge')
		challenge_type = get_challenge_type(challenge)
		score = request.form.get('time')
		comment = request.form.get('comment')
		# bad user input handling
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
		en = Entry([score, datetime_to_string(datetime.today()), comment]).to_json()
		user_id = get_user_id(username)
		challenges = user.challenges
		try:
			# there is already an entry for the challenge. append the entry to the list
			if verbose:
				print('adding challenge to dict for database. Challenge is: '+ challenge) 
			challenges[challenge].append(en)
		except KeyError:
			# there is no entry for that challenge yet. Create a list for it and add the entry
			challenges[challenge] = [en]
		# this clears the dict for that user. It seemed to fix everything when it was not working
		reset_user_challenges(username)
		user.challenges = challenges
		db.session.add(user)
		db.session.commit()
		return redirect('/'+username+'/records-view')
	return render_template('user/personal_records_add.html',challenge_dict=challenge_dict, user=user, username=username)

@app.route('/<username>/records-view')
@login_required
def records_view(username):
	user = User.query.filter_by(username=username).first()
	ch = json_to_objects(user.challenges)
	return render_template('user/personal_records_view.html',challenge_dict=challenge_dict,username=username,user=user, ch=ch)

@app.route('/<username>/suggest-challenge',methods=['GET','POST'])
@login_required
def suggest_challenge(username):
	user = User.query.filter_by(username=username).first()
	if request.method == "POST":
		challenge_type = request.form.get('type')
		challenge_name = request.form.get('challenge')
		already_exists = Suggestion.query.filter_by(name=challenge_name).first()
		if already_exists:
			flash(f'That Challenge was already suggested by {User.query.get(already_exists.user_id).first_name}')
			return render_template('user/new_challenge.html',username=username, user=user)
		challenge = Suggestion(
						type=challenge_type,
						name=challenge_name,
						user_id=user.id
					)
		send_emails = read('args.txt')['email']
		
		# save suggestion to database
		db.session.add(challenge)
		db.session.commit()

		if send_emails == True:
			send_email_to_somebody('Challenge submission',repr(challenge_submission),'devin.s.shende@gmail.com')
			send_email_to_somebody('Challenge submission',repr(challenge_submission),'ravi.sameer.shende@gmail.com')
		else:
			if verbose:
				print('would be sending emails but that was set to False so not doing that.')
		return render_template('user/home.html', username=username, user=user)
	return render_template('user/new_challenge.html',username=username, user=user)

@app.route('/siteadmin/')
def admin_login():
	if verbose: print('Admin home page')
	return render_template('siteadmin/admin_home.html',username='stillworkingonusername')

@app.route('/siteadmin/suggestions')
def admin_suggestions():
	if verbose: print('Admin see suggestions page')
	# suggestions=read('challenge_suggestions.txt')
	suggestions = Suggestion.query.all()
	return render_template('siteadmin/admin_suggestions.html',json=suggestions,username='stillworkingonusername')

@app.route('/<username>/profile')
@login_required
def profile(username):
	user = User.query.filter_by(username=username).first()
	return render_template('user/profile.html', user=user, username=username)

@app.route('/<username>/profile/edit', methods=['GET','POST'])
@login_required
def edit_profile(username):
	user = User.query.filter_by(username=username).first()
	if request.method == 'POST':
		# file uploading for profile pic
		if 'photo' in request.files and request.files['photo'].filename != '':
			print('you uploaded a photo!')
			# if filename == '' then the user didn't actually enter an image
			filename = f'{user.id}.jpg'
			if filename in os.listdir(PROF_PICS_PATH):
				# user already has a profile pic. delete the old one then add the new one.
				path = os.path.join(PROF_PICS_PATH, filename)
				if verbose:
					print(f'{user} has already entered a profile pic \nOverwriting it by removing {filename} from {PROF_PICS_PATH}')
				os.remove(path)
			if verbose:
				print(f'saving uploaded profile pic as {filename}')
			actual_name = photos.save(request.files['photo'], name=filename)
			assert filename == actual_name, f'filenames did not match: {filename} and {actual_name}'

		first_name 	= request.form.get( 'first_name' )
		last_name 	= request.form.get( 'last_name'  )
		gender 		= request.form.get( 'gender'     )
		bday 		= request.form.get( 'day'       )
		bmonth 		= request.form.get( 'month'     )
		byear 		= request.form.get( 'year'     )
		if not gender:
			gender = user.gender
		birthday = datetime(year=int(byear), month=int(bmonth), day=int(bday))
		age = datetime.today().year - birthday.year
		user.first_name = first_name
		user.last_name 	= last_name
		user.gender 	= gender
		user.birthday = birthday
		# print(user.first_name, user.last_name, user.age, user.gender,sep='\n')
		db.session.add(user)
		db.session.commit()
		return redirect('/'+username+'/profile')
	return render_template('user/profile_edit.html', user=user, username=username, months=monthsDict)


@app.route('/img')
def imgview():
	user = User.query.filter_by(username='hihi').first()
	return render_template('img.html',user=user, username='hihiasdfasd')

