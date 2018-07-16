from flask_restful import Resource, reqparse
from models.accountRequest import AccountRequestModel

class AccountRequest(Resource):

    # class global paraser filter
    parser = reqparse.RequestParser()
    # the expected arguments:
    parser.add_argument('Data', # required
        type=dict,
        required=True,
        location='json',
        help="This field cannot be left blank!")
    parser.add_argument('Risk', # required
        type=dict,
        required=True,
        location='json',
        help="This field cannot be left blank!")

# POST /account-Requests
# The API allows the AISP to ask an ASPSP to create a new account-request resource.
#
# * allows the AISP to send a copy of the consent to the ASPSP
#  to authorise access to account and transaction information.
# * The ASPSP creates the account-request resource and responds with a unique
#  AccountRequestId to refer to the resource.
# * Prior to calling the API, the AISP must have an access token issued
#  by the ASPSP using a client credentials grant.

    def post(self):
        data = AccountRequest.parser.parse_args()
        # check input data
        # * Permission
        # * ExpirationDateTime
        # * TransactionFromDateTime
        # * TransactionToDateTime
        account, error = AccountRequestModel.createAccountRequest(data['Data'], data['Risk'])

        if not account:
            return {'message':error}, 400 # bad request
        try:
            account.save_to_db()
        except:
            return {'message' : 'An error occured saving the item.'}, 500 # internal server error

        # responde with
        # * AccountRequestId
        # * status
        # * CreationDateTime
        # * Permission
        # * ExpirationDateTime
        # * TransactionFromDateTime
        # * TransactionToDateTime
        return account.json(), 201 # item created

    def get(self, accountRequestId):
        # check if such request id exist and verify the status
        account = AccountRequestModel.findAccountRequestById(accountRequestId)

        if not account:
            return {'message' : 'Item not found'}, 404 # Item not found (this is not documented in OB spec)
        # some test cases here
        elif account.status == 'AwaitingAuthorisation':
            AccountRequestModel.AuthorizeAccountRequestId(accountRequestId)
        elif account.status == 'Authorised':
        #    AccountRequestModel.RevokeAccountRequestId(accountRequestId)
        #elif account.status == 'Revoked':
            AccountRequestModel.RejecteAccountRequestId(accountRequestId)
        return account.json(), 200 # OK

    def delete(self, accountRequestId):
        # check if such request id exist and verify the status
        account = AccountRequestModel.findAccountRequestById(accountRequestId)
        if not account:
            return {'message' : 'Item not found'}, 404 # Item not found (this is not documented in OB spec)
        #account.delete_from_db()
        AccountRequestModel.RevokeAccountRequestId(accountRequestId)
        return account.json(), 200 # OK
