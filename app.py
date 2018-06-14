import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import (
		UserRegister,
		UserLogin,
		UserLogout
	)
from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.secret_key = 'mySecretKeyHere' # or use: app.config['JWT_SECRET_KEY']

api = Api(app)
jwt = JWTManager(app)

# JWT config and loaders...

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	return decrypted_token['jti'] in BLACKLIST # checks if id is on the balcklist

@jwt.invalid_token_loader # invalid token was provided
def invalid_token_callaback(error):
	return jsonify ({
		'description' : 'Signature verification failed.',
		'error' : 'invalid_token'
		}), 401

# End-Points available
api.add_resource(UserRegister, '/register') # a new user registration
api.add_resource(UserLogin, '/login') # allows user to loging
api.add_resource(UserLogout, '/logout') # allows user to logout

# allow these executions only when its called directly
if __name__ == '__main__':
	from db import db
	db.init_app(app)

	@app.before_first_request
	def create_tables():
		db.create_all()

	app.run(port=5000, debug = True)