#import dateutil.parser
from db import db

status = ['Rejected', 'AwaitingAuthorisation', 'Authorised', 'Revoked']

class AccountRequestModel(db.Model):

    __tablename__ = 'AccountRequests'
    id = db.Column(db.Integer, primary_key=True)
    accountRequestId = db.Column(db.String(128))
    status = db.Column(db.String)
    expiration = db.Column(db.String)
    transactionFrom = db.Column(db.String)
    transactionTo = db.Column(db.String)
    creationDateTime = db.Column(db.String)

    #permissions = db.Column(db.ARRAY(db.String()), server_default='[]') # Warrning! ARRAY suppoert by postgresql only
    _permissions = db.Column(db.String)
    @property
    def permissions(self):
        return [permission for permission in self._permissions.split(';')]

    @permissions.setter
    def permissions(self, value):
        iterator = 0
        for item in value:
            if not iterator:
                self._permissions = item
            else:
                self._permissions += ';' + item
            iterator += 1

    def __init__(self, permissions, expiration, transactionFrom, transactionTo):
        self.permissions = permissions
        # e.g. "2017-05-02T00:00:00+00:00"
        self.expiration = expiration #dateutil.parser.parse(expiration)
        self.transactionFrom = transactionFrom #dateutil.parser.parse(transactionFrom)
        self.transactionTo = transactionTo #dateutil.parser.parse(transactionTo)
        self.risk = None
        self.links = None
        self.meta = None

        self.status = status[1] # starts with AwaitingAuthorisation
        self.creationDateTime = '2017-05-02T00:00:00+00:00' #TODO

    @classmethod
    def createAccountRequest(cls, data, risk):

        accountRequest = None
        error = None
        try:
            # required
            # persmissions list []
            permissions = data['Permissions']
        except:
            error = 'Permissions parameter is missing. '
            return accountRequest, error

        try:
            # optional
            # e.g. "2017-05-02T00:00:00+00:00"
            expiration = data['ExpirationDateTime'] #dateutil.parser.parse(expiration)
        except:
            expiration = None

        try:
            # optional
            # e.g. "2017-05-02T00:00:00+00:00"
            transactionFrom = data['TransactionFromDateTime']
        except:
            transactionFrom = None

        try:
            # optional
            # e.g. "2017-05-02T00:00:00+00:00"
            transactionTo = data['TransactionToDateTime']
        except:
            transactionTo = None

        accountRequest = cls(permissions, expiration, transactionFrom, transactionTo)

        accountRequest.accountRequestId = '88379' # TODO

        alreadyExist = AccountRequestModel.findAccountRequestById(accountRequest.accountRequestId)
        if alreadyExist:
            accountRequest = None
            if alreadyExist.status == status[3]: # revoked
                # TODO for test purpose
                alreadyExist.status = status[1]
            error = 'Request already exists'
            return alreadyExist, error

        if accountRequest:
            accountRequest.risk = risk  #TODO
            accountRequest.links = {'Self': '/account-requests/{}'.format(accountRequest.accountRequestId)} #TODO
            accountRequest.meta = {'TotalPages': 1} #TODO

        return accountRequest, error

    @classmethod
    def AuthorizeAccountRequestId(cls, arId):
        account = cls.query.filter_by(accountRequestId=arId).first()
        if account:
            account.status = status[2]
            account.save_to_db()
        # TODO may need to return some operation status

    @classmethod
    def RevokeAccountRequestId(cls, arId):
        account = cls.query.filter_by(accountRequestId=arId).first()
        if account:
            account.status = status[3]
            account.save_to_db()
        # TODO may need to return some operation status

    @classmethod
    def RejecteAccountRequestId(cls, arId):
        account = cls.query.filter_by(accountRequestId=arId).first()
        if account:
            account.status = status[0]
            account.save_to_db()
        # TODO may need to return some operation status

    @classmethod
    def findAccountRequestById(cls, arId):
        account = cls.query.filter_by(accountRequestId=arId).first()
        if account:
            account.risk = {}
            account.links = {'Self': '/account-requests/{}'.format(account.accountRequestId)}
            account.meta = {'TotalPages': 1}
        return account

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
		         'Data' : {
                     'AccountRequestId' : self.accountRequestId,
                     'Status' : self.status,
                     'CreationDateTime' : self.creationDateTime,
                     'Permissions' : self.permissions,
                     'ExpirationDateTime' : self.expiration,
                     'TransactionFromDateTime' : self.transactionFrom,
                     'TransactionToDateTime' : self.transactionTo
                 },
		         'Risk' : self.risk,
		         'Links' : self.links,
                 'Meta' : self.meta
	    }
