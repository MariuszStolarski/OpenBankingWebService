from db import db

class UserModel(db.Model):

	# usin SQLAlchemy prepare for Database
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80)) # with lengh limitation to 80 characters
	password = db.Column(db.String(80)) # with lengh limitation to 80 characters

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def json(self):
		return {
			'id' : self.id,
			'username' : self.username
		}

	# saving user to the database via SQLAlchemy
	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	# finding user in the database by username
	@classmethod
	def find_by_username(cls, username):
		return cls.query.filter_by(username=username).first()
