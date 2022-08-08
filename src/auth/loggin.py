import google.auth.transport.requests
import google.oauth2.id_token 
import os
import logging

HTTP_REQUEST = google.auth.transport.requests.Request()

class User : 
    def __init__(self,tokenID,Id,data) : 
        self.tokenID = tokenID
        self.data = data
        self.Id = Id

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.Id)
    def get_data(self): 
        return self.data
    @staticmethod
    def get(id,data) : 
        return User("",id,data)

    @staticmethod
    def loadFormToken(tokenId) : 
        claims = google.oauth2.id_token.verify_firebase_token(
        tokenId, HTTP_REQUEST, audience=os.environ.get('GOOGLE_CLOUD_PROJECT'))
        if not claims:
            return None
        id = claims['sub']
        logging.getLogger('user').debug("sub ID : %s",format(id))
        return User(tokenId,id,None)  
        

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal