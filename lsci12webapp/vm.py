from google.appengine.ext import db

class VM(db.Model):
    
    ip = db.StringProperty()
    vmtype = db.StringProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()
    result = db.FloatProperty()
    
    def __str__(self):
        return '\
        VM\r\n\
        ip: '+self.ip+'\r\n\
        vmtype: '+self.vmtype+'\r\n\
        paraSigma '+str(self.paraSigma)+'\r\n\
        paraEA '+str(self.paraEA)+'\r\n\
        result '+str(self.result)
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'result': self.result}
        return s