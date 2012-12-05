from google.appengine.ext import db

class Param(db.Model):
    
    index = db.IntegerProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()

    def getJSON(self):
        s = {'index': self.index, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA}
        return s
    