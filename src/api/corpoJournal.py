from flask_restful import Resource, Api, fields,marshal,reqparse
from flask_login import current_user
from eveGateway.eveProxy import ProxyCaracter,EveGatewayCaching
from eveGateway.ssotools import EveSSO
from eveGateway.CropoWalletProxy import CorporationWalletProxy,CorporationWalletJournalProxy
from itertools import islice

_dataFiled = {}
_dataFiled["id"] = fields.String(attribute='id')
_dataFiled["ref_type"] = fields.String(attribute='ref_type')
_dataFiled["context_name"] = fields.String(attribute='context_name')
_dataFiled["amount"] = fields.String(attribute='amount')
_dataFiled["description"] = fields.String(attribute='description')

_resourceFields = {}
_resourceFields["draw"] = fields.String(attribute='draw', default = '1')
_resourceFields["recordsTotal"] = fields.String(attribute='recordsTotal')
_resourceFields["recordsFiltered"] = fields.String(attribute='recordsFiltered')
_resourceFields["data"] = fields.List(fields.Nested(_dataFiled))

class ApiCorpoJournal(Resource) : 

    def __init__(self, eveGatewayCache):
        self.eveGatewayCache = eveGatewayCache

    def get(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('length',type=int,location='args') 
        parser.add_argument('draw',type=int,location='args') 
        args = parser.parse_args() 
        _sso: EveSSO = self.eveGatewayCache.getSso(current_user.get_id())
        _carac: ProxyCaracter = self.eveGatewayCache.getCaracter(current_user.get_id())
        _walletJournal = CorporationWalletJournalProxy(_carac.corporation_id,1,_sso)
        _walletJournal.getDataFromEve()
        ret = {}
        ret["draw"] = args['draw']
        _nbrRecord = 0 
        if 'length' in  args :
            _nbrRecord = args['length']
            l = []
            for d in islice(_walletJournal.journal,args['length']) :
                l.append(d)
            ret["data"] =  l
        else : 
            ret["data"] =  _walletJournal.journal
            _nbrRecord = len(_walletJournal.journal)
        ret["recordsTotal"] = _nbrRecord
        ret["recordsFiltered"] = _nbrRecord    
        
        return marshal(ret, _resourceFields)

    def put(self) : 
        parser = reqparse.RequestParser()
        parser.add_argument('carcId',type=int,location='args') 
        parser.add_argument('corpoID',type=int,location='args') 
        _args = parser.parse_args() 
        _sso: EveSSO = self.eveGatewayCache.getSso(_args['carcId'])
        _walletJournal = CorporationWalletJournalProxy(_args['corpoId'],1,_sso)
        _walletJournal.synch()
 
