from flask_restful import Resource, Api

class ApiCorpoJournal(Resource) : 
    def get(self):
        ret = dict()
        ret["draw"] = 1
        ret["recordsTotal"] = 100
        ret["recordsFiltered"] = 100
        d = list()

        for id   in range(0,100) : 
            obj = dict()
            obj["id"] = id
            obj["ref_type"] ="a"
            obj["context_name"]="a"
            obj["amount"]="a"
            obj["description"]="a"
            d.append(obj)
        ret["data"] = d
        
        return ret
        
