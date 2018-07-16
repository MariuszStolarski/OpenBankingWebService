import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import (
		UserRegister,
		UserLogin,
		UserLogout,
		TokenRefresh
	)
from resources.accountRequest import AccountRequest
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

@jwt.invalid_token_loader # invalid token was provided (e.g. when user did log out)
def invalid_token_callaback(error):
	return jsonify ({
		'description' : 'Signature verification failed.',
		'error' : 'invalid_token'
		}), 401

@jwt.expired_token_loader
def expired_token_callabak():
	return jsonify({
		'description' : 'The token has expired',
		'error' : 'token_expired'
		}), 401

@jwt.needs_fresh_token_loader # token is correct but it is not the fresh one
def token_not_fresh_callaback():
	return jsonify ({
		'description' : 'The token is not fresh.',
		'error' : 'fres_token_required'
		}), 401

@jwt.revoked_token_loader # token is no longer valid (e.g. when user did log out)
def revoked_token_callaback():
	return jsonify ({
		'description' : 'The token has been revoked.',
		'error' : 'token_revoked'
		}), 401

# End-Points available
api.add_resource(UserRegister, '/register') # a new user registration
api.add_resource(UserLogin, '/login') # allows user to loging
api.add_resource(UserLogout, '/logout') # allows user to logout
api.add_resource(TokenRefresh, '/refresh')

# Open Banking Account and Transaction ASPSP API issued for AISP / PISP
# (Account Servicing Payment Service Provider)
# * expected URI: /TheBank/open-banking/v1.0/payments

# Accont-resuests
# Allows the AISP to send a copy of the consent to the ASPSP
# to authorise access to account and transaction information
# ASPSP responds with a unique AccountRequestId to refer to the resource
# Prior to calling the API, the AISP must have an access token
# issued by the ASPSP using a client credentials grant
# * POST /account-requests
api.add_resource(AccountRequest, '/account-requests', '/account-requests/<string:accountRequestId>')
# * GET /account-requests/{AccountRequestId}
# * DELETE /account-requests/{AccountRequestId}


# # GET /acconts


# allow these executions only when its called directly
if __name__ == '__main__':
	from db import db
	db.init_app(app)

	@app.before_first_request
	def create_tables():
		db.create_all()

	app.run(port=5000, debug = True)
