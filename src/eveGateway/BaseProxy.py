import enum
import json
import logging
import urllib
from enum import Enum, unique

import requests
from requests import HTTPError
from eveGateway.ssotools import EveSSO, SSOException

class ProxyException(Exception):
    def __init__(self, message :str):
        self.message = message




class ProxyEve : 
    def __init__(self, sso : EveSSO) : 
        if sso == None or sso.access_token == None:
            raise ProxyException("ProxyEve - init : sso is empty")
        self.sso = sso
    
    def request(self,url) -> dict: 
        jsonData :dict  = None
        try:
            headers = {"Authorization": "Bearer {}".format(self.sso.access_token)}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            jsonData = res.json()    
        except HTTPError as e:
            logging.getLogger().debug(
                "ProxyEve - init - Fail to get url %s, response code is: %s",url,
                    res.status_code
                )
            
            raise SSOException("ProxyEve - init - Fail to get {}".format(url))
        return jsonData