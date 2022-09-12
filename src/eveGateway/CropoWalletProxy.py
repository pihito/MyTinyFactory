import enum

from dataclasses import dataclass
from re import T

from eveGateway.BaseProxy import ProxyEve, ProxyException
from eveGateway.ssotools import EveSSO, SSOException
from enum import Enum, unique

@unique
class ProxyWalletDivisionField(Enum) :
    f_balance = "balance"
    f_division  = "division"

@unique
class proxyWalletDivisionNameField(Enum) : 
    f_division : str = "division"
    f_name : str = "name"
    f_wallet = "wallet"
    f_hangar =  "hangar"


@unique 
class proxyWalletJournalField(Enum) :
    f_amount = "amount"
    f_balance = "balance"
    f_context_id =  "context_id"
    f_context_name =  "context_name"
    f_context_id_type = "context_id_type"
    f_date =  "date"
    f_description = "description"
    f_first_party_id = "first_party_id"
    f_first_party_name= "first_party_name"
    f_id ="id"
    f_reason = "reason"
    f_ref_type = "ref_type"
    f_second_party_id = "second_party_id"
    f_second_party_name = "second_party_name"
    f_tax = "tax"
    f_tax_receiver_id  ="tax_receiver_id"
    f_tax_receiver_name = "tax_receiver_name"
 
class CorporationWalletProxy (ProxyEve): 
    _corpo_id: str = None
    _walletdivision : dict = dict()
    _walletdivisionName : dict = dict()

    def __init__(self, corpo_id : str, sso : EveSSO ) : 
        super().__init__(sso)
        self._corpo_id = corpo_id
        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}/wallets".format(
                    corpo_id
                )
            )
        temp = self.request(url_path,True)
        
        for d in temp : 
            self._walletdivision[d[ProxyWalletDivisionField.f_division.value]] = d[ProxyWalletDivisionField.f_balance.value]
        
        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}/divisions".format(
                    corpo_id
                )
            )
        temp = self.request(url_path,True)
        for d in temp[proxyWalletDivisionNameField.f_wallet.value] : 
           
            if proxyWalletDivisionNameField.f_name.value in d : 
                self._walletdivisionName[d[proxyWalletDivisionNameField.f_name.value]] = d[proxyWalletDivisionNameField.f_division.value]
            else : 
                if d[proxyWalletDivisionNameField.f_division.value] == 1 : 
                    self._walletdivisionName["main wallet"] = d[proxyWalletDivisionNameField.f_division.value] 
                else : 
                    self._walletdivisionName[proxyWalletDivisionNameField.f_division.value] = d[proxyWalletDivisionNameField.f_division.value]
    def getDivision(self, division : int) -> int : 
        ret = None
        if division in self._walletdivision : 
            ret = self._walletdivision[division]
        return ret
    
    def getDivisionByName(self, divisionName : str) -> int : 
        ret = None
        if divisionName in self._walletdivisionName: 
            ret = self._walletdivision[_walletdivisionName[divisionName]]

    def is_division(self,division : int) ->bool :
        return  division in self._walletdivision
    
    def is_divisionName(self, division : str) ->bool : 
        return division in self._walletdivisionName
    
    @property 
    def divisionKeys(self) : 
        return self._walletdivision.keys

    @property
    def allDivision(self) : 
        return self._walletdivision
    
    @property
    def allDivisionByName(self) : 
        ret  = dict()
        for name, number in self._walletdivisionName.items() : 
            ret[name] = self._walletdivision[number]
        return ret
        
    @property
    def division1(self) -> int : 
        return self.getDivision(1)
    @property
    def division2(self) -> int : 
        return self.getDivision(2)
    @property
    def division3(self) -> int : 
        return self.getDivision(3)
    @property
    def division4(self) -> int : 
        return self.getDivision(4)
    @property
    def division5(self) -> int : 
        return self.getDivision(5)
    @property
    def division6(self) -> int : 
        return self.getDivision(6)
    @property
    def division7(self) -> int : 
        return self.getDivision(7)

    
class CorporationWalletJournalProxy (ProxyEve): 
    _corpo_id: str = None
    _url_path : str = """sumary_line"""
    _walletNumber : str = None
    _walletJournal = list()

    def __init__(self, corpo_id : str, wallet: str,sso : EveSSO ) : 
        super().__init__(sso)
        self._corpo_id = corpo_id
        self._walletNumber = wallet
        page = 1
        end = False
        while end == False :
            try : 
                self._url_path: str = (
                    "https://esi.evetech.net/latest/corporations/{}/wallets/{}/journal/?page={}".format(
                        corpo_id,wallet,page
                    )
                )
                self._walletJournal = self._walletJournal + (self.request(self._url_path,True))
                page= page +1
            except ProxyException : 
                end = True
             
        #retrieve id to complete the data
        ids = set()
        for d in self._walletJournal : 
            if proxyWalletJournalField.f_context_id.value in d : 
                ids.add(d[proxyWalletJournalField.f_context_id.value])
            ids.add(d[proxyWalletJournalField.f_first_party_id.value])
            ids.add(d[proxyWalletJournalField.f_second_party_id.value])
            if proxyWalletJournalField.f_tax_receiver_id.value in d : 
                ids.add(d[proxyWalletJournalField.f_tax_receiver_id.value])
        self._url_path: str = ("https://esi.evetech.net/latest/universe/names/")
        l = list(ids)
        names = self.requestPost(self._url_path,l)
        namesById  = dict()
        for n in names : 
            namesById[ n["id"]]   = n["name"]

        for d in self._walletJournal :
            if proxyWalletJournalField.f_context_id.value in d : 
                d[proxyWalletJournalField.f_context_name.value] = namesById[d[proxyWalletJournalField.f_context_id.value]]
            else : 
                d[proxyWalletJournalField.f_context_name.value]  =""
            d[proxyWalletJournalField.f_first_party_name.value] = namesById[d[proxyWalletJournalField.f_first_party_id.value]]
            d[proxyWalletJournalField.f_second_party_name.value] = namesById[d[proxyWalletJournalField.f_second_party_id.value]]
            if proxyWalletJournalField.f_tax_receiver_id.value in d : 
                d[proxyWalletJournalField.f_tax_receiver_name.value] = namesById[d[proxyWalletJournalField.f_tax_receiver_id.value]]
            else : 
                d[proxyWalletJournalField.f_tax_receiver_name.value] = ""

    @property
    def journal(self) : 
        return self._walletJournal
