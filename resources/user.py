from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
		create_access_token, 
		create_refresh_token,
		jwt_required,
		get_raw_jwt
	)
from blacklist import BLACKLIST

# class global paraser filter
_user_parser = reqparse.RequestParser()
# lets filter only expected arguments
_user_parser.add_argument('username', 
	type=str, 
	required=True, 
	help="This field cannot be left blank!")

_user_parser.add_argument('password', 
	type=str, 
	required=True, 
	help="This field cannot be left blank!")

# user registration 
class UserRegister(Resource):

	# handle POST method for user registration .../register
	def post(self):
		data = _user_parser.parse_args()
		if UserModel.find_by_username(data['username']):
			# the user already exist
			return {'message' : 'User already exist'}, 400
		# create new user
		user = UserModel(**data)
		# save user to the database
		user.save_to_db()

		return {'message' : 'User created sucessfully.'}, 201

# user login
class UserLogin(Resource):
	
	@classmethod
	def post(cls):
		# get user from parser
		data = _user_parser.parse_args()

		# find user in database
		user = UserModel.find_by_username(data['username'])

		# check password
		if user and safe_str_cmp(user.password, data['password']):
			#TODO: should we verify if user already logged in?
			access_token = create_access_token(identity=user.id, fresh=True)
			refresh_token = create_refresh_token(user.id)

			return {
				'access_token' : access_token,
				'refresh_token' : refresh_token
			}, 200

		return {'message' : 'Invalid credentials'}, 401

# user logout
class UserLogout(Resource):
	@jwt_required # only for loged in users
	def post(self):
		# use balaclist current token instead of user id
		jti = get_raw_jwt()['jti'] # jti is "JWT ID", an unique identifier for JWT
		BLACKLIST.add(jti)
		return {'message' : 'Sucessfully logged out.'}, 200