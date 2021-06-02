DBENV = 'dev'
# DBENV = 'prod'

# UNFINISHED BUSINESS FOR PERSONAL RECORDS
'''
styling of table and layout
handle bad input from users for the score field in form
'''

# libraries
from flask import Flask, render_template, request, redirect, url_for, flash
from termcolor import colored
from datetime import date
import ast
import os
import argparse
from pyfiglet import figlet_format
# my imports
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, PROF_PICS_PATH, ADMIN_PASSWORD
from challenges import *
from utils import *
# flask extensions
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from flask_admin import Admin
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import BaseModelView, typefmt
from flask_admin.base import AdminIndexView, expose
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate


def get_admin_auth():
	return read('args.txt')['admin_auth']
def write_admin_auth(TF):
	if type(TF) != bool:
		raise ValueError('please only enter a boolean value to write_admin_auth')
	args = read('args.txt')
	args['admin_auth'] = TF
	write('args.txt',args)

app = Flask(__name__)

app.static_folder = 'static'
app.secret_key = 'jsahgfdjshgfsdjgghayfdsajhsfdayda'
app.jinja_env.globals.update(get_best=get_best)
app.jinja_env.globals.update(get_challenge_type=get_challenge_type)
app.jinja_env.globals.update(to_name_case=to_name_case)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(ChallengeTypes=ChallengeTypes)
from datetime import datetime

app.jinja_env.globals.update(today=datetime.today)

if DBENV == 'dev':
	# development mode
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
	app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

else:
	# production mode
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wcowsukvvbcixu:f469d73d4ff15e8e827136950649d1870834f9df6870cc679a61c9fdb3e437e3@ec2-54-243-44-102.compute-1.amazonaws.com:5432/d2e6lq83t6rpad'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# UPLOAD_FOLDER = '/database/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# photos = UploadSet('photos',IMAGES)
# app.config['UPLOADED_PHOTOS_DEST'] = 'static/profile_pics'
# app.config['FLASK_APP_FILE'] = 'app.py'
# configure_uploads(app,photos)

# FLASK MIGRATE - for dealing with Database changes better
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)
 
class User(db.Model, UserMixin):
	id 			= db.Column(db.Integer, primary_key=True)
	first_name 	= db.Column(db.String(40), nullable=False)
	last_name 	= db.Column(db.String(40), nullable=False)
	age 		= db.Column(db.Integer, nullable=False)
	birthday	= db.Column(db.DateTime, nullable=False)
	gender 		= db.Column(db.String(15), nullable=False)
	username 	= db.Column(db.String(20), unique=True, nullable=False)
	password 	= db.Column(db.String(40), nullable=False)
	profile 	= db.Column(db.String(20), default='1')
	security_question_id = db.Column(db.String(100), nullable=False)
	security_question_ans = db.Column(db.String(50), nullable=False)
	challenges 	= db.Column(db.PickleType, default={})

	def __repr__(self):
		return '<User %r>' % self.username

	def get_profile_pic(self):
		path = None
		filename = str(self.id) + '.jpg'
		if filename in os.listdir(PROF_PICS_PATH):
			if DBENV != 'dev':
				path = os.path.join('../..',PROF_PICS_PATH,filename)
		if not path:
			path = '../../static/blank_profile.jpg'
		return path

	def format_bday(self):
		return self.birthday.strftime('%b %d, %Y')

	def get_age(self):
		from datetime import datetime
		age = datetime.today().year - self.birthday.year
		return age


app.jinja_env.globals.update(User=User)
app.jinja_env.cache = {}
# hopefully this will bring better loading speeds 
# https://blog.socratic.org/the-one-weird-trick-that-cut-our-flask-page-load-time-by-70-87145335f679

class Suggestion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(10), nullable=False)
	name = db.Column(db.String(30), unique=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	def __repr__(self):
		return '<Suggestion %r>' % self.name

def date_format(view, value):
	return value.strftime('%b %d, %Y')

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
		type(None): typefmt.null_formatter,
		date: date_format
	})

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class UserView(ModelView):
	column_display_pk = True # controls whether id is (not) hidden
	column_searchable_list = ('first_name','last_name')
	column_exclude_list = ('password','security_question_ans')
	column_type_formatters = MY_DEFAULT_FORMATTERS # formats bday
	can_delete = False
	can_create = False

	def is_accessible(self):
		# only shows home page when set to False
		# shows normal admin page with full access when set to True
		return get_admin_auth()

class MyModelView(ModelView):
	column_type_formatters = MY_DEFAULT_FORMATTERS
	page_size = 10
	column_display_pk = True
	# column_labels = dict(first_name='Name ', last_name='Last Name')
	# self.can_create=False
	
	def is_accessible(self):
		# only shows home page when set to False
		# shows normal admin page with full access when set to True
		return get_admin_auth()

class MyHomeView(AdminIndexView):
	@expose('/',methods=('GET','POST'))
	def index(self):
		if request.method == 'POST':
			print('posting.')
			if get_admin_auth():
				# log them out
				print('making it unallowed. they hit logout')
				write_admin_auth(False)
				return render_template('admin/myhome.html',auth=get_admin_auth())
			# they are entering the password
			entered_password = request.form.get('password')
			if entered_password == ADMIN_PASSWORD.decoded:
				# let them in. The password entered is correct
				print('you are authenticated!')
				write_admin_auth(True)
				return self.render('admin/myhome.html',auth=True, n_suggested_chs=len(Suggestion.query.all()))
			# don't let them in: the password entered is incorrect
			flash(f"password: \"{request.form.get('password')}\" is incorrect")
			return self.render('admin/myhome.html',auth=False)
		else:
			if get_admin_auth():
				# they are authenticated but did not just submit the login form. Let them in
				return render_template('admin/myhome.html',auth=True, n_suggested_chs=len(Suggestion.query.all()))
		# admin login screen
		return self.render('admin/myhome.html',auth=get_admin_auth())

admin = Admin(app, index_view=MyHomeView(), template_mode='bootstrap3')


# admin = Admin(app, template_mode='bootstrap3') # template mode is styling
admin.add_view(UserView(User, db.session))
# Unnecessary with site admin being a thing
# admin.add_view(MyModelView(Suggestion, db.session))

# heroku = Heroku(app)

# this import must be after initialization of Flask(__name__)
from views import *
if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	# if user types --email at the end of python3 app.py, then it will be set to true
	# if user doesn't say --email, it will be set to false
	
	# parser.add_argument('-e','--email',action='store_true')
	# parser.add_argument('-v','--verbose',action='store_true')
	# COMMENT = ''
	# args = parser.parse_args()
	# write('args.txt',{'email':args.email,'verbose':args.verbose,'admin_auth':False})
	# if args.verbose:
	# 	print(' * Send emails:',colored(str(args.email),'green' if args.email else 'red'))
	# 	print(' * Verbose:', colored('True','green'))

	# # CHANGE THIS LINE TO STOP GETTING EMAILS
	# args.email = True
	if DBENV == 'dev':
		response = input(colored("do you want verbose mode enabled? (y for yes, enter for no):\n",'cyan'))
		if response == "y":
			write('args.txt',{'email':False,'verbose':True,'admin_auth':False})
			print(' * Verbose:', colored('True','green'))
		else:
			write('args.txt',{'email':False,'verbose':False,'admin_auth':False})
			print(' * Verbose:', colored('False','red'))


	# fonts: bulbhead, slant, computer
	# http://www.figlet.org/examples.html
	print(figlet_format('NW Ninja Park',font="slant"))
	print(figlet_format('challenge tracker'))
	print(' * DBENV: ', colored(DBENV, 'cyan'))
	# print(' * Send emails:',colored(str(args.email),'green' if args.email else 'red'))
	# print(' * Verbose:', colored(str(args.verbose),'green' if args.email else 'red'))
	manager.run() # for flask-migrate
	# app.run()

	