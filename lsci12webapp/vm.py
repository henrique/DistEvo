from google.appengine.ext import db

class VM(db.Model):
    
    ip = db.StringProperty()
    vmtype = db.StringProperty()
    dateUpdate = db.DateTimeProperty(auto_now_add=True)
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype}
        return s
    
    def __repr__(self):
        return "ip: "+str(self.ip)+" vmtype: "+str(self.vmtype)
    
    def set(self, vm):
        self.ip = vm['ip']
        self.vmtype = vm['vmtype']
