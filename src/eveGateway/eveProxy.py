import json
import logging
import urllib
from enum import Enum, unique

import requests
from requests import HTTPError
from eveGateway.ssotools import EveSSO, SSOException

class ProxyException(Exception):
    def __init__(self, message):
        self.message = message


@unique
class EveRequest(Enum):
    SSO = 1
    CARACTER = 2

class ProxyCaracter:
    PX64 = "px64x64"
    PX128 = "px128x128"
    PX256 = "px256x256"
    PX512 = "px512x512"

    def __init__(self, sso : EveSSO):
        if sso == None or sso.access_token == None:
            raise ProxyException("init : sso is empty")
        self.sso = sso
        self._photoUrls = None
        try:
            headers = {"Authorization": "Bearer {}".format(self.sso.access_token)}
            blueprint_path = "https://esi.evetech.net/latest/characters/{}".format(
                sso.character_id
            )
            res = requests.get(blueprint_path, headers=headers)
            res.raise_for_status()
            jsonData = res.json()
            self.data = jsonData
            headers = {"Authorization": "Bearer {}".format(self.sso.access_token)}
            blueprint_path = (
                "https://esi.evetech.net/latest/characters/{}/portrait/".format(
                    sso.character_id
                )
            )
            res = requests.get(blueprint_path, headers=headers)
            res.raise_for_status()
            jsonData = res.json()
            self._photoUrls = jsonData
        except HTTPError as e:
            self.logger.debug(
                "ProxyCaracter - init - Fail to get caracter, SSO response code is: {}".format(
                    sso_response.status_code
                )
            )
            raise SSOException("ProxyCaracter - init - Fail to get caracter")

    def getPhotoUrl(self, taille : str ="px64x64" ) -> str:
        return self._photoUrls[taille]

        
    """classe pour créer un cache des connexion sso de eve et des requêtes : 
    Caracter

    L'index de première clès du cache est l'id du caractère

    Raises:
        ProxyException: _description_
        SSOException: _description_

    """
class EveGatewayCaching:
    
    caracCache : dict = {}

    def __init__(self):
        pass

    def AddCarater(self, eveId : str, eveSso : EveSSO) :
        self.caracCache[eveId] = dict()
        self.caracCache[eveId][EveRequest.SSO] = eveSso

    def getSso(self, eveId : str) -> EveSSO :
        if eveId in self.caracCache:
            return self.caracCache[eveId][EveRequest.SSO]
        return None

    def getCaracter(self, eveId : str) ->ProxyCaracter : 
        if eveId in self.caracCache:
            cache = self.caracCache[eveId]
            if EveRequest.CARACTER in cache:
                return self.caracCache[eveId][EveRequest.CARACTER]
            else:
                proxy = ProxyCaracter(self.cache[EveRequest.SSO])
                self.caracCache[eveId][EveRequest.CARACTER] = proxy
                return proxy
        return None
 

