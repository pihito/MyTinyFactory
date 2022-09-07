import enum

from dataclasses import dataclass

from eveGateway.BaseProxy import ProxyEve, ProxyException
from eveGateway.ssotools import EveSSO, SSOException


@enum.unique
class ProxyWalletDivisionField(Enum) :
    f_balance = "balance"
    f_division  = "division"

@enum.unique
class proxyWalletDivisionNameField(Enum) : 
    f_division : str = "division"
    f_name : str = "name"

class corporationWalletProxy (ProxyEve): 
    
    _corpo_id: str = None
    _walletdivision : dict = dict()
    _walletdivisionName : dict = dict()

    def __init__(self, corpo_id : str, sso : EveSSO ) : 
        super.__init___(sso)
        self._corpo_id = corpo_id
        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}/wallets".format(
                    corpo_id
                )
            )
        temp = self.request(url_path)
        
        for d in temp : 
            self._walletdivision[d[ProxyWalletDivisionField.f_division.value]] = d[ProxyWalletDivisionField.f_balance.value]
        
        url_path: str = (
                "https://esi.evetech.net/latest/corporations/{}/divisions".format(
                    corpo_id
                )
            )
        temp = self.request(url_path)
        for d in temp.wallet : 
            self._walletdivisionName[d[proxyWalletDivisionNameField.f_name.value]] = d[proxyWalletDivisionNameField.f_division.value]

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

    

