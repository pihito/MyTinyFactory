import enum
import json
import logging
import urllib
from enum import Enum, unique

import requests
from requests import HTTPError
from eveGateway.ssotools import EveSSO, SSOException

class ProxyException(Exception):
    def __init__(self, message :str,code):
        self.message = message




class ProxyEve : 
    def __init__(self, sso : EveSSO) : 
        if sso == None or sso.access_token == None:
            raise ProxyException("ProxyEve - init : sso is empty")
        self.sso = sso
    
    def requestPost(self,url,payload,auth = False) -> dict :
        jsonData :dict  = None
        try:
            headers : dict[str,str] = {"accept": "application/json","Content-Type": "application/json","Cache-Control": "no-cache"}
            if auth == True :  
                headers["Authorization"] = "Bearer {}".format(self.sso.access_token)
            res = requests.post(url, headers=headers,json  = payload)
            res.raise_for_status()
            jsonData = res.json()    
        except HTTPError as e:
            logging.getLogger().debug(
                "ProxyEve - init - Fail to get url %s, response code is: %s",url,
                    res.status_code
                )
            
            raise ProxyException("ProxyEve - init - Fail to get {}".format(url),res.status_code)
        return jsonData

    def request(self,url,auth = False) -> dict: 
        jsonData :dict  = None
        try:
            headers : dict[str,str] = {"accept": "application/json","Content-Type": "application/json","Cache-Control": "no-cache"}
            if auth == True :  
                headers["Authorization"] = "Bearer {}".format(self.sso.access_token)
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            jsonData = res.json()    
        except HTTPError as e:
            logging.getLogger().debug(
                "ProxyEve - init - Fail to get url %s, response code is: %s",url,
                    res.status_code
                )
            
            raise ProxyException("ProxyEve - init - Fail to get {}".format(url),res.status_code)
        return jsonData