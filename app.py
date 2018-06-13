import os

from flask import Flask
from flask_restful import Api

from resources.user import UserRegister

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['PROPAGATE_EXCEPTIONS'] = True

api = Api(app)

# End-Points available
api.add_resource(UserRegister, '/register') # a new user registration

# allow these executions only when its called directly
if __name__ == '__main__':
	from db import db
	db.init_app(app)

	@app.before_first_request
	def create_tables():
		db.create_all()

	app.run(port=5000, debug = True)