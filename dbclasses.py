from app import db, app
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