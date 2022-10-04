from distutils import core
from datetime import datetime
import enum

from dataclasses import dataclass
from heapq import merge
from multiprocessing.sharedctypes import Value
from re import T
from wsgiref.handlers import format_date_time

from eveGateway.BaseProxy import ProxyEve, ProxyException
from eveGateway.ssotools import EveSSO, SSOException
from enum import Enum, unique
from firebase_admin import firestore

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
    f_ana_axis1 = "ana_axis1"
    f_AAAAMM = "AAAAMM"
    f_AAAAMMDD = "AAAAMMDD"
 
class CorporationWalletProxy (ProxyEve): 
    _corpo_id: str = None
    _walletdivision : dict = dict()
    _walletdivisionName : dict = dict()

    def __init__(self, corpo_id : str, sso : EveSSO, db ) : 
        super().__init__(sso)
        self._corpo_id = corpo_id
        self._db = db
        
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
            ret = self._walletdivision[self._walletdivisionName[divisionName]]

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

    def __init__(self, corpo_id : str, wallet: str,sso : EveSSO,db ) : 
        super().__init__(sso)
        self._corpo_id = corpo_id
        self._walletNumber = wallet
        self._db = db
        

    def getDataFromEve(self) : 
        page = 1
        end = False
        while end == False :
            try : 
                self._url_path: str = (
                    "https://esi.evetech.net/latest/corporations/{}/wallets/{}/journal/?page={}".format(
                        self._corpo_id,self._walletNumber,page
                    )
                )
                self._walletJournal = self._walletJournal + (self.request(self._url_path,True))
                page= page +1
            except ProxyException : 
                end = True
             
        #retrieve id to complete the data
        ids = set()
        _contextType = ["market_transaction_id", "industry_job_id", "contract_id", "type_id" ]
        for d in self._walletJournal : 
            if  proxyWalletJournalField.f_context_id.value in d and proxyWalletJournalField.f_context_id_type.value in d and d[proxyWalletJournalField.f_context_id_type.value] not in _contextType : 
                
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
            if proxyWalletJournalField.f_context_id.value in d and d[proxyWalletJournalField.f_context_id.value] in namesById : 
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
   
    def addAnafield(self) : 
        _type : dict[str, str]= {"bounty_prizes":	"Prine",
                "agent_mission_time_bonus_reward": "Prine",
                "agent_mission_reward": "Prine",
                "corporate_reward_payout": "Incu + Fob",
                "project_discovery_reward": "Discovery",
                "market_escrow": "Marché",
                "contract_price": "contrat",
                "contract_brokers_fee_corp": "contrat",
                "corporation_account_withdrawal": "Transfert",
                "office_rental_fee": "Location bureau",
                "inheritance": "other",
                "industry_job_tax": "industrie",
                "manufacturing": "industrie",
                "player_donation": "don",
                "transaction_tax": "Marché",
                "market_transaction": "Marché",
                "alliance_maintainance_fee": "other",
                "asset_safety_recovery_tax": "other",
                "advertisement_listing_fee": "other",
                "brokers_fee": "Marché"}
        ret = {}
        for d in self._walletJournal : 
            if d [proxyWalletJournalField.f_ref_type.value] in _type : 
                d[proxyWalletJournalField.f_ana_axis1.value] = _type[ d[proxyWalletJournalField.f_ref_type.value] ]
                ldate = d[proxyWalletJournalField.f_date.value]
                d[proxyWalletJournalField.f_AAAAMM.value] = ldate[0:3] + ldate[4:6]
                d[proxyWalletJournalField.f_AAAAMMDD.value] = d[proxyWalletJournalField.f_AAAAMM.value] + ldate[7:8]

   
    def synch(self) : 
        #on vérifie que des donnée existe 
        corpoDataRef = self._db.document(u'CorpoWallet/{}'.format(self._corpo_id))
        corpoData = corpoDataRef.get()
        if not corpoData.exists : 
            #création du document corporation et wallet
            d = {'corpo_id':self._corpo_id}
            self._db.collection(u'CorpoWallet').add(document_id = str(self._corpo_id), document_data=d)
            corpoDataRef = self._db.document(u'CorpoWallet/{}'.format(self._corpo_id))
            r: CollectionReference = corpoDataRef.collection("1")
            r.add({ 'wallet' : 1 })
            r =corpoDataRef.collection("2") 
            r.add({ 'wallet' : 2 })
            r = corpoDataRef.collection("3")
            r.add({ 'wallet' : 3 })
            r = corpoDataRef.collection("4")
            r.add({ 'wallet' : 4 })
            r = corpoDataRef.collection("5") 
            r.add({ 'wallet' : 5 })
            r = corpoDataRef.collection("6")
            r.add({ 'wallet' : 6 })
            r = corpoDataRef.collection("7") 
            r.add({ 'wallet' : 7 })
           
        #récupération du full set eve
        self.getDataFromEve()
        #ajout des champs analytique
        self.addAnafield()
        
        #sauvegarde dans la DB
        #walletDataRef = self._db.document(u'CorpoWallet/{}/{}'.format(self._corpo_id,self._walletNumber))
        walletDataRef = self._db.document(u'CorpoWallet/98665675/1')
        for d in self._walletJournal : 
            walletDataRef.collection(u'transactions').document(d[proxyWalletJournalField.f_id]).set(d)
            
       



