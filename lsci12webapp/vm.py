from google.appengine.ext import db

class VM(db.Model):
    
    ip = db.StringProperty()
    vmtype = db.StringProperty()
    dateUpdate = db.DateTimeProperty(auto_now_add=True)
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype, 'dateUpdate': str(self.dateUpdate)}
        return s
    
    def __repr__(self):
        return "ip: "+str(self.ip)+" vmtype: "+str(self.vmtype)+" dateUpdate: "+str(self.dateUpdate)
    
    def set(self, vm):
        self.vmtype = vm['vmtype']
