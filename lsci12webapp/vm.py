from google.appengine.ext import db

class VM(db.Model):
    
    ip = db.StringProperty()
    vmtype = db.StringProperty()
    jobId = db.IntegerProperty()
    dateUpdate = db.DateTimeProperty(auto_now_add=True)
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype, 'jobId': self.jobId}
        return s
    
    def __repr__(self):
        return "ip: "+str(self.ip)+" vmtype: "+str(self.vmtype)+" jobId: "+str(self.jobId)
    
    def set(self, vm):
        self.ip = vm['ip']
        self.vmtype = vm['vmtype']
        self.jobId = vm['jobId']
