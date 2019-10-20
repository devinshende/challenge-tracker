# libraries
from flask import Flask, render_template, request, redirect, url_for, flash
from pprint import pprint
from termcolor import colored
from datetime import datetime, date
import ast
import os
import argparse
# my imports
from utils import *
from mylib.cipher import encode, decode
from constants import SECURITY_QUESTIONS, PROF_PICS_PATH, ADMIN_PASSWORD
from challenges import Entry
# flask extensions
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from flask_admin import Admin
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import BaseModelView, typefmt
from flask_admin.base import AdminIndexView, expose
from flask_heroku import Heroku
from flask_uploads import UploadSet, configure_uploads, IMAGES

# UNFINISHED BUSINESS FOR PERSONAL RECORDS
'''
styling of table and layout
handle bad input from users for the score field in form
'''
admin_authenticated = False
app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'jsahgfdjshgfsdjgghayfdsajhsfdayda'
app.jinja_env.globals.update(get_best=get_best)
app.jinja_env.globals.update(get_challenge_type=get_challenge_type)
app.jinja_env.globals.update(to_name_case=to_name_case)
app.jinja_env.globals.update(len=len)
from datetime import datetime
app.jinja_env.globals.update(today=datetime.today)

# UPLOAD_FOLDER = '/database/profile_pics'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

photos = UploadSet('photos',IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/profile_pics'
configure_uploads(app,photos)

class User(db.Model, UserMixin):
	id 			= db.Column(db.Integer, primary_key=True)
	first_name 	= db.Column(db.String(20), nullable=False)
	last_name 	= db.Column(db.String(20), nullable=False)
	age 		= db.Column(db.Integer, nullable=False)
	birthday	= db.Column(db.DateTime, nullable=False)
	gender 		= db.Column(db.String(6), nullable=False)
	username 	= db.Column(db.String(20), unique=True, nullable=False)
	password 	= db.Column(db.String(40), nullable=False)
	security_question_id = db.Column(db.Integer, nullable=False)
	security_question_ans = db.Column(db.String(50), nullable=False)
	challenges 	= db.Column(db.PickleType, default={})

	def __repr__(self):
		return '<User %r>' % self.username

	def get_profile_pic(self):
		filename = str(self.id) + '.jpg'
		if filename in os.listdir(PROF_PICS_PATH):
			path = os.path.join('../..',PROF_PICS_PATH,filename)
		else:
			path = '../../static/blank_profile.jpg'
		print(f'profile pic source is {repr(path)}')
		return path

	def format_bday(self):
		return self.birthday.strftime('%b %d, %Y')

	def get_age(self):
		from datetime import datetime
		age = datetime.today().year - self.birthday.year
		return age


app.jinja_env.globals.update(User=User)

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

class UserView(ModelView):
	column_display_pk = True # controls whether id is (not) hidden
	column_searchable_list = ('first_name','last_name')
	column_exclude_list = ('password','security_question_id','security_question_ans')
	column_type_formatters = MY_DEFAULT_FORMATTERS # formats bday
	
	def is_accessible(self):
		# only shows home page when set to False
		# shows normal admin page with full access when set to True
		return admin_authenticated

class MyModelView(ModelView):
	column_type_formatters = MY_DEFAULT_FORMATTERS
	page_size = 10
	column_display_pk = True
	# column_labels = dict(first_name='Name ', last_name='Last Name')
	# self.can_create=False
	
	def is_accessible(self):
		# only shows home page when set to False
		# shows normal admin page with full access when set to True
		return admin_authenticated

class MyHomeView(AdminIndexView):
	@expose('/',methods=('GET','POST'))
	def index(self):
		global admin_authenticated
		if request.method == 'POST':
			print('posting.')
			if admin_authenticated:
				# log them out
				print('making it unallowed. they hit logout')
				admin_authenticated = False
				return render_template('admin/myhome.html',auth=admin_authenticated)
			# they are entering the password
			entered_password = request.form.get('password')
			if entered_password == ADMIN_PASSWORD.decoded:
				print('you are authenticated!')
				admin_authenticated = True	
				return self.render('admin/myhome.html',auth=admin_authenticated)
			return "password: \"" + str(request.form.get('password')) + "\"\n is incorrect" + \
			"<br><hr><a href='/admin'>try again</a>"
		else:
			if admin_authenticated:
				# normal home page
				return render_template('admin/myhome.html',auth=admin_authenticated)
		return self.render('admin/myhome.html',auth=admin_authenticated)

admin = Admin(app, index_view=MyHomeView(), template_mode='bootstrap3')


# admin = Admin(app, template_mode='bootstrap3') # template mode is styling
admin.add_view(UserView(User, db.session))
admin.add_view(MyModelView(Suggestion, db.session))
# admin.add_view(MyModelView(Challenge, db.session))
#something with @action to accept challenges

heroku = Heroku(app)

# this import must be after initialization of Flask(__name__)
from views import *
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# if user types --email at the end of python3 app.py, then it will be set to true
	# if user doesn't say --email, it will be set to false
	parser.add_argument('-e','--email',action='store_true')
	parser.add_argument('-v','--verbose',action='store_true')
	COMMENT = ''
	args = parser.parse_args()
	write('args.txt',{'email':args.email,'verbose':args.verbose})
	if args.verbose:
		print(' * Send emails:',colored(str(args.email),'green' if args.email else 'red'))
		print(' * Verbose:', colored('True','green'))
	app.run()
