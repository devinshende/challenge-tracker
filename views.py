from app import *
from utils import *
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort, jsonify
from mylib.cipher import encode, decode
from mylib.mail import send_email_to_somebody
from constants import *
from challenges import Entry
from pprint import pprint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
import json
from termcolor import cprint

try:
	verbose = read('args.txt')['verbose']
except KeyError:
	verbose = False

#   __  _           _          _          __  __ 
#  / _|| | __ _ ___| | __  ___| |_ _   _ / _|/ _|
# | |_ | |/ _` / __| |/ / / __| __| | | | |_| |_ 
# |  _|| | (_| \__ \   <  \__ \ |_| |_| |  _|  _|
# |_|  |_|\__,_|___/_|\_\ |___/\__|\__,_|_| |_|  

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

#                          _   _     
#  _   _ _ __   __ _ _   _| |_| |__  
# | | | | '_ \ / _` | | | | __| '_ \ 
# | |_| | | | | (_| | |_| | |_| | | |
#  \__,_|_| |_|\__,_|\__,_|\__|_| |_|  

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
	SECURITY_QUESTIONS = load_security_questions()
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
			if limit_input_size(name=first_name, max_size=20):
				return redirect('/signup')
			if limit_input_size(name=last_name, max_size=20):
				return redirect('/signup')
			age = request.form.get('age')
			if check_negative(age) != False:
				return redirect('/signup')
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
			if limit_input_size(name=username, max_size=20, item="username"):
				return render_template('unauth/signup2.html', security_questions=SECURITY_QUESTIONS)
			if limit_input_size(name=password, max_size=40, item="password"):
				return render_template('unauth/signup2.html', security_questions=SECURITY_QUESTIONS)
			confirm_password = request.form.get('confirm_password')
			security_question = request.form.get('security_question')
			answer = request.form.get('answer')
			if limit_input_size(name=answer, max_size=50, item="answer"):
				print(f'username is {username}')
				return render_template('unauth/signup2.html', username=username, password=password, confirm_password=confirm_password, security_questions=SECURITY_QUESTIONS, security_question=security_question)

			security = {'question':security_question,'answer':encode(answer)}
			users_lst = list(users)[:-1] # all but current one which is only partly signed up.
			for user in users_lst:
				if verbose:
					print(user)
					print('username: ',user.username)
					print(user.username == username)
				if user.username == username:
					flash('That username is already taken')
					return render_template("unauth/signup2.html", password=password, confirm_password=confirm_password, security_questions=SECURITY_QUESTIONS, security_question=security_question, answer=answer)

			variables = read('vars.txt')
			v = variables['half_user']
			print('half user is ',v)
			print('half user\'s month is ',v['month'])
			
			max_uid = 0
			for u in users:
				if max_uid < u.id:
					max_uid = u.id 
			id = max_uid + 1
			
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
			 			security_question_id=security['question'],
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

@app.route('/leaderboard', methods=['GET','POST'])
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
			brackets = get_brackets(data, selected_challenge_type)
			return render_template('unauth/leaderboard_brackets.html', tables=brackets, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				brackets=brackets, bracket_names=BRACKETS)
		else:
			sorted_data = sort_data(data, selected_challenge_type)
			print('no brackets')
			return render_template('unauth/leaderboard_no_brackets.html', data=sorted_data, header=selected_challenge, \
				challenge_type=to_name_case(selected_challenge_type), \
				checked=repr(checked))
	return render_template('unauth/leaderboard_no_brackets.html',challenge_dict=load_challenge_dict(),header="Leaderboard")

#  _   _ ___  ___ _ __ 
# | | | / __|/ _ \ '__|
# | |_| \__ \  __/ |   
#  \__,_|___/\___|_|   

@app.route('/<username>/')
@login_required
def home(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	name = user.first_name
	return render_template('user/home.html', username=username, user=user)

@app.route('/forgot-password', methods=['GET','POST'])
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
			question = user.security_question_id
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
				question = user.security_question_id
				if verbose: 
					print('answers do not match')
					print('question is ',question)
				flash('Incorrect Answer')
				return render_template('unauth/forgot_password.html', username=username, security_question=question)
		if password:
			if limit_input_size(name=password, max_size=40, item="password"):
				return redirect('/forgot-password')
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

#		 ____  ____  ___  _____  ____  ____   ___ 
#		(  _ \( ___)/ __)(  _  )(  _ \(  _ \ / __)
#		 )   / )__)( (__  )(_)(  )   / )(_) )\__ \
#		(_)\_)(____)\___)(_____)(_)\_)(____/ (___/

@app.route('/<username>/records-add', methods=['GET','POST'])
@login_required
def records_add(username):
	user = User.query.filter_by(username=username).first()
	# user = db.session.query(User).filter_by(username=username).first()
	if request.method == "POST":
		challenge = request.form.get('challenge')
		challenge_type = get_challenge_type(challenge)
		score = request.form.get('score')
		if check_negative(score) != False:
				return redirect('/'+username+'/records-add')
		if score == None:
			raise ValueError("look at line 344 in records_add in views.py - score is None")
		comment = request.form.get('comment')
		# bad user input handling
		if challenge_type == ChallengeTypes.time:
			try:
				score = float(score)
			except ValueError:
				flash('Please enter a number for your time')
				return redirect('/'+username+'/records-add')
		if challenge_type in [ChallengeTypes.reps, ChallengeTypes.laps]:
			try:
				score = int(score)
			except ValueError:
				flash('Please enter a whole number for ' + challenge_type)
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
	return render_template('user/records/add.html',challenge_dict=load_challenge_dict(), user=user, username=username)

@app.route('/<username>/records-view')
@login_required
def records_view(username):
	user = User.query.filter_by(username=username).first()
	ch = json_to_objects(user.challenges)
	return render_template('user/records/view.html',challenge_dict=load_challenge_dict(),username=username,user=user, ch=ch)

@app.route('/<username>/records-delete', methods=['GET','POST'])
@login_required
def records_delete(username):
	user = User.query.filter_by(username=username).first()
	challenges = user.challenges
	if request.method == "POST":
		challenge_type = request.form.get("challenge")
		try:
			del challenges[challenge_type]
			if verbose: print(f'after deleting {challenge_type}, challenges is now {challenges}')
		except KeyError:
			flash("unable to delete data for the challenge:"+challenge_type)
		reset_user_challenges(user.username)
		user.challenges = challenges
		db.session.add(user)
		db.session.commit()
		return redirect('/'+user.username+'/records-view')
	ch = json_to_objects(user.challenges)
	return render_template('user/records/delete.html',challenge_dict=load_challenge_dict(),username=username,user=user, ch=challenges)

@app.route('/<username>/suggest-challenge', methods=['GET','POST'])
@login_required
def suggest_challenge(username):
	user = User.query.filter_by(username=username).first()
	if request.method == "POST":
		challenge_type = request.form.get('type')
		challenge_name = request.form.get('challenge_name')

		# force challenge names to be less than 30 characters
		if limit_input_size(name=challenge_name, max_size=30):
			return redirect(f'/{username}/suggest-challenge')
		
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
			try:
				body = f"""{user.first_name} {user.last_name} suggested a new challenge: 
				{repr(challenge_name)}
				of the type \"{challenge_type}\"

				Thanks, 
				- Ninja Park Tracker"""
				send_email_to_somebody('Challenge submission',body,'devin.s.shende@gmail.com')
				send_email_to_somebody('Challenge submission',body,'ravi.sameer.shende@gmail.com')
			except:
				cprint('Error sending email','red')
		
		return render_template('user/home.html', username=username, user=user) # redirect home after submitting
	return render_template('user/new_challenge.html',username=username, user=user)

@app.route('/<username>/leaderboard', methods=['GET','POST'])
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
	return render_template('user/leaderboard_no_brackets.html',challenge_dict=load_challenge_dict(), header="Leaderboard", \
		username=username, user=user)

# 		 ____  ____  _____  ____  ____  __    ____ 
# 		(  _ \(  _ \(  _  )( ___)(_  _)(  )  ( ___)
# 		 )___/ )   / )(_)(  )__)  _)(_  )(__  )__) 
# 		(__)  (_)\_)(_____)(__)  (____)(____)(____)

@app.route('/<username>/profile')
@login_required
def profile(username):
	user = User.query.filter_by(username=username).first()
	return render_template('user/profile.html', user=user, username=username)

@app.route('/<username>/profile/edit', methods=['GET','POST'])
@login_required
def edit_profile(username):
	from app import DBENV
	user = User.query.filter_by(username=username).first()
	if request.method == 'POST':
		# file uploading for profile pic
		photo_obj = request.files['photo']
		if 'photo' in request.files and photo_obj.filename != '':
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
			if DBENV == 'prod':
				actual_name = photos.save(photo_obj, name=filename)
				assert filename == actual_name, f'filenames did not match: {filename} and {actual_name}'
				crop_img(filename)
				flash('You may need to refresh the page to see the updated profile picture')
			else:
				flash('refusing to upload that image cause this is dev mode')

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

@app.route('/<username>/profile/delete_account', methods=['GET','POST'])
@login_required
def profile_delete(username):
	auth = False
	user = User.query.filter_by(username=username).first()
	if request.method == 'POST':
		entered_password = request.form.get('password')
		if entered_password:
			# "enter your password"
			if entered_password == decode(user.password):
				auth = True
			else:
				flash('incorrect password!')
				return redirect(f'/{username}/profile/edit')
		else:
			# "are you sure?"
			flash('Deleted account for user '+username)        
			os.remove('static/profile_pics/'+str(user.id)+'.jpg')
			logout_user()
			delete_user(user)
			return redirect('/')
	return render_template(
		'user/delete_account.html',
		username=username,
		user=user,
		auth=auth
		)

@app.route('/refresh')
def refresh():
	return jsonify({'success':True})

#            _           _       
#   __ _  __| |_ __ ___ (_)_ __  
#  / _` |/ _` | '_ ` _ \| | '_ \  
# | (_| | (_| | | | | | | | | | |
#  \__,_|\__,_|_| |_| |_|_|_| |_|

from adminviews import *


