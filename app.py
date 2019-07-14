from flask import Flask, render_template, request, redirect
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, question_to_id, id_to_question
from pprint import pprint

#UNFINISHED BUSINESS FOR SIGNUPS
'''
REQUIRE ALL FIELDS
User friendly message when passwords don't match instead of reloading page
feedback to show that user was successfully added
write a test function to see that all fields were entered for the user before assuming user is properly entered
work on login?

json file to keep track of users instead of having them only alive until program is rerun
styles to make it look not awful
'''


app = Flask(__name__)
app.static_folder = 'static'

users = {
	
}

@app.route('/')
def home():
	return render_template('home.jinja2') # kwargs are used for jinja2

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		first_name = request.form.get('firstName')
		last_name = request.form.get('lastName')
		age = request.form.get('age')
		gender = request.form.get('gender')
		user_id = len(users)

		users[user_id] = {
			'user_id':user_id,
			'firstname':first_name,
			'lastname':last_name,
			'age':age,
			'gender':gender
		}
		return redirect('/signup/2')
	return render_template('signup.jinja2')


@app.route('/signup/2', methods=['GET','POST'])
def signup2():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		if password != confirm_password:
			print('passwords did not match')
			return redirect("/signup/2") # shouldn't just redirect. Should have user message			
		security_question = request.form.get('security_question')
		security_question_id = question_to_id(security_question) # convert string of question to it's id in SECURITY_QUESTIONS
		answer = request.form.get('answer')
		security = {'id':security_question_id,'answer':answer}
		
		user_id = len(users) - 1
		users[user_id]['username'] = username
		users[user_id]['password'] = encode(password)
		users[user_id]['security_question'] = security
		pprint(users)
	return render_template('signup2.jinja2', security_questions = SECURITY_QUESTIONS)


@app.route('/login')
def login():
	return 'login here'

@app.route('/leaderboard')
def leaderboard():
	return 'Riley Cvitanich wins'

app.run()
