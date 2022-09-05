import enum
import json
import logging
import urllib
from enum import Enum, unique

import requests
from requests import HTTPError

from eveGateway.BaseProxy import ProxyEve,ProxyException
from eveGateway.ssotools import EveSSO, SSOException


@unique
class EveRequest(Enum):
    SSO = 1
    CARACTER = 2
    CORPO =3
    ALLIANCE = 4


@unique 
class EvePictureSize(Enum) : 
    PX64 = "px64x64"
    PX128 = "px128x128"
    PX256 = "px256x256"
    PX512 = "px512x512"



@unique
class ProxyAllianceField(Enum) :
    f_creator_corporation_id = "creator_corporation_id"
    f_creator_id = "creator_id"
    f_date_founded = "date_founded"
    f_executor_corporation_id = "executor_corporation_id"
    f_faction_id = "faction_id"
    f_name = "name"
    f_ticker = "ticker"

class ProxyAlliance(ProxyEve) : 
    
    _allianceData : dict = None
    _allianceIcon : dict = None
    
    def __init__(self, sso : EveSSO, allianceId :str) : 
        super().__init__(sso)

        url_path: str = (
                "https://esi.evetech.net/latest/alliances/{}".format(
                    allianceId
                )
            )
        self._allianceData : dict = self.request(url_path)
        url_path: str = (
                "https://esi.evetech.net/latest/alliances/{}/icons".format(
                    allianceId
                )
            )
        self._allianceIcon : dict = self.request(url_path)

    @property        
    def alllianceData(self) -> dict : 
        return self._allianceData
      
    @property
    def creator_corporation_id(self)->str : 
        return self._allianceData[ProxyAllianceField.f_creator_corporation_id.value]

    @property
    def creator_id(self)->str : 
        return self._allianceData[ProxyAllianceField.f_creator_id.value]

    @property
    def date_founded(self)->str : 
        return self._allianceData[ProxyAllianceField.f_date_founded.value]

    @property
    def executor_corporation_id(self)->str : 
        ret :str = ""
        if ProxyAllianceField.f_executor_corporation_id.value in self._allianceData :
            ret = self._allianceData[ProxyAllianceField.f_executor_corporation_id.value]
        return ret 

    @property
    def faction_id(self)->str : 
        ret : str = ""
        if ProxyAllianceField.f_faction_id in self._allianceData : 
            ret =  self._allianceData[ProxyAllianceField.f_faction_id.value]
            return ret 

    @property
    def name(self)->str : 
        return self._allianceData[ProxyAllianceField.f_name.value]

    @property
    def ticker(self)->str : 
        return self._allianceData[ProxyAllianceField.f_ticker.value]
        
    def getAllianceIcon(self,size = EvePictureSize.PX64) -> str : 
        ret : str = ""
        if size == EvePictureSize.PX64 or size == EvePictureSize.PX128 :
            ret = self._allianceIcon[size]
        return ret
    
    @property
    def iconPX64(self) -> str :
        return  self._allianceIcon[EvePictureSize.PX64]
    
    @property
    def iconPX128(self) -> str :
        return  self._allianceIcon[EvePictureSize.PX128]

class ProxyCorpoField(Enum):
    f_alliance_id ="alliance_id"
    f_ceo_id = "ceo_id"
    f_creator_id = "creator_id"
    f_date_founded = "date_founded"
    f_description	 = "description"
    f_faction_id = "faction_id"
    f_home_station_id = "home_station_id"
    f_member_count = "member_count"
    f_name ="name"
    f_shares = "shares"
    f_tax_rate = "tax_rate"
    f_ticker = "ticker"
    f_url	= "url"
    f_war_eligible = "war_eligible"

class ProxyCropo(ProxyEve) : 
    
    _corpoData : dict = None
    _corpoIcon : dict = None
    
    def __init__(self, sso : EveSSO, CorpoId :str) : 
        super().__init__(sso)

        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}".format(
                    CorpoId
                )
            )
        self._corpoData : dict = self.request(url_path)
        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}/icons".format(
                    CorpoId
                )
            )
        self._corpoIcon : dict = self.request(url_path)

    @property
    def corpoData(self)  -> dict: 
        return self._corpoData
   
    @property
    def corpoIncon(self,size = EvePictureSize.PX64) -> dict : 
        return self._corpoIcon[size]
    
    @property
    def alliance_id(self) ->str :
        ret : str = None
        if ProxyCorpoField.f_alliance_id.value in self._corpoData : 
            ret =  self._corpoData[ProxyCorpoField.f_alliance_id.value]
        return ret
    
    @property
    def ceo_id(self) ->str :
        return self._corpoData[ProxyCorpoField.f_ceo_id.value]
    
    @property
    def creator_id(self) ->str :
        return self._corpoData[ProxyCorpoField.f_creator_id.value]
    
    @property
    def date_founded(self) ->str :
        return self._corpoData[ProxyCorpoField.f_date_founded.value]
    
    @property
    def description(self) ->str :
        return self._corpoData[ProxyCorpoField.f_description.value]
    
    @property
    def faction_id(self) ->str :
        ret : str = None
        if ProxyCorpoField.f_faction_id.value in self._corpoData : 
            ret = self._corpoData[ProxyCorpoField.f_faction_id.value]
        return ret
    
    @property
    def home_station_id(self) ->str :
        return self._corpoData[ProxyCorpoField.f_home_station_id.value]
    
    @property
    def member_count(self) ->str :
        return self._corpoData[ProxyCorpoField.f_member_count.value]
    
    @property
    def name(self) ->str :
        return self._corpoData[ProxyCorpoField.f_name.value]
    
    @property
    def shares(self) ->str :
        return self._corpoData[ProxyCorpoField.f_shares.value]
    
    @property
    def tax_rate(self) ->str :
        return self._corpoData[ProxyCorpoField.f_tax_rate.value]
    
    @property
    def ticker(self) ->str :
        return self._corpoData[ProxyCorpoField.f_ticker.value]
    
    @property
    def url(self) ->str :
        return self._corpoData[ProxyCorpoField.f_url.value]
    
    @property
    def war_eligible(self) ->str :
        return self._corpoData[ProxyCorpoField.f_war_eligible.value]
    
    def get_corpoIcon(self,size = EvePictureSize.PX64) -> str :
        ret : str = ""
        if size != EvePictureSize.PX512 :
            ret = self._corpoIcon[size]
        return ret
    
    @property
    def iconPX64(self) -> str :
        return  self._corpoIcon[EvePictureSize.PX64]
    
    @property
    def iconPX128(self) -> str :
        return  self._corpoIcon[EvePictureSize.PX128]
    
    @property
    def iconPX256(self) -> str :
        return  self._corpoIcon[EvePictureSize.PX256]

class ProxyCaracterField(Enum): 
    f_alliance_id = "alliance_id"
    f_birthday = "birthday"
    f_bloodline_id = "bloodline_id"
    f_corporation_id = "corporation_id"
    f_description = "description"
    f_faction_id = "faction_id"
    f_gender = "gender"
    f_name = "name"
    f_security_status = "security_status"
    f_title = "title"
    f_protrait = "protrait"

class ProxyCaracter:
    PX64 = "px64x64"
    PX128 = "px128x128"
    PX256 = "px256x256"
    PX512 = "px512x512"

    sso : EveSSO = None
    _photoUrls : dict = None
    _data : dict = None
    _corpo : ProxyCropo = None
    _alliance : ProxyAlliance = None 

    def __init__(self, sso : EveSSO):
        if sso == None or sso.access_token == None:
            raise ProxyException("init : sso is empty")
        self.sso = sso
        
        try:
            #information de base sur le caractère
            headers = {"Authorization": "Bearer {}".format(self.sso.access_token)}
            blueprint_path = "https://esi.evetech.net/latest/characters/{}".format(
                sso.character_id
            )
            res = requests.get(blueprint_path, headers=headers)
            res.raise_for_status()
            self._data = res.json()
            
            #récupération des Urls de protrait
            headers = {"Authorization": "Bearer {}".format(self.sso.access_token)}
            blueprint_path = (
                "https://esi.evetech.net/latest/characters/{}/portrait/".format(
                    sso.character_id
                )
            )
            res = requests.get(blueprint_path, headers=headers)
            res.raise_for_status()
            self._photoUrls = res.json()

            #récupération de la corpo
            self._corpo : ProxyCropo = ProxyCropo(self.sso,self.corporation_id)

            #récupération de l'alliance si existante
            if(self.alliance_id != None or self.alliance_id != "") :
                self._alliance : ProxyAlliance = ProxyAlliance(self.sso,self.alliance_id)

         
        except HTTPError as e:
            self.logger.debug(
                "ProxyCaracter - init - Fail to get caracter, SSO response code is: {}".format(
                    res.status_code
                )
            )
            raise SSOException("ProxyCaracter - init - Fail to get caracter")

    def getPhotoUrl(self, taille : str ="px64x64" ) -> str:
        return self._photoUrls[taille]

    @property
    def data(self) : 
        return self._data
    
    @property
    def alliance_id(self) ->str:
        ret : str = None
        if(ProxyCaracterField.f_alliance_id.value in self._data) : 
            ret =  self._data[ProxyCaracterField.f_alliance_id.value] 
        return ret
    
    @property
    def birthday(self) ->str: 
        return self._data[ProxyCaracterField.f_alliance_id.value]

    @property
    def bloodline_id(self) ->str: 
        return self._data[ProxyCaracterField.f_bloodline_id.value]
    
    @property
    def corporation_id (self) ->str:
        return self._data[ProxyCaracterField.f_corporation_id.value]

    @property
    def description  (self) ->str:
        return self._data[ProxyCaracterField.f_description.value]
    
    @property
    def faction_id  (self) ->str:
        return self._data[ProxyCaracterField.f_faction_id.value]
    
    @property
    def gender  (self) ->str:
        return self._data[ProxyCaracterField.f_gender.value]

    @property
    def name  (self) ->str:
        return self._data[ProxyCaracterField.f_name.value]

    @property
    def security_status  (self) ->str:
        return self._data[ProxyCaracterField.f_security_status.value]

    @property
    def title  (self) ->str:
        return self._data[ProxyCaracterField.f_title.value]

    @property
    def protrait64px (self) ->str:
        return self._photoUrls[self.PX64]
    
    @property
    def protrait128px (self) ->str:
        return self._photoUrls[self.PX128]
    
    @property
    def protrait256px (self) ->str:
        return self._photoUrls[self.PX256]

    @property
    def protrait512px (self) ->str:
        return self._photoUrls[self.PX512]

    @property
    def corporation(self) -> ProxyCropo : 
        return self._corpo

    @property
    def alliance(self) -> ProxyAlliance : 
        return self._alliance

    @property
    def eveId(self) -> str : 
        return self.sso.character_id

    """classe pour créer un cache des connexion sso de eve et des requêtes : 
    Caracter

    L'index de première clès du cache est l'id du caractère

    Raises:
        ProxyException: _description_
        SSOException: _description_

    """
class EveGatewayCaching:
    
    _caracCache : dict = {}

    def __init__(self):
        pass

    def AddCarater(self, eveId : str, eveSso : EveSSO) :
        self._caracCache[eveId] = dict()
        self._caracCache[eveId][EveRequest.SSO] = eveSso

    def getSso(self, eveId : str) -> EveSSO :
        if eveId in self._caracCache:
            return self._caracCache[eveId][EveRequest.SSO]
        return None

    def getCaracter(self, eveId : str) ->ProxyCaracter : 
        if eveId in self._caracCache:
            cache : dict = self._caracCache[eveId]
            if EveRequest.CARACTER in cache:
                return cache[EveRequest.CARACTER]
            else:
                proxy = ProxyCaracter(cache[EveRequest.SSO])
                self._caracCache[eveId][EveRequest.CARACTER] = proxy
                return proxy
        return None
    




