from flask_restful import Resource, reqparse
from models.user import UserModel

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