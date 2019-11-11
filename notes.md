app.py

    app = Flask(__name__)
    db = SQLAlchemy(app)
    ...
    from dbclasses import User

dbclasses.py
	
	from app import db
	class User(db.Model):
		def __init__(self):
			blah blah blah