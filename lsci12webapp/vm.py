from google.appengine.ext import db

class VM(db.Model):
    
    ip = db.StringProperty()
    vmtype = db.StringProperty()
    jobId = db.IntegerProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()
    result = db.FloatProperty()
    
    def getJSON(self):
        s = {'ip': self.ip, 'vmtype': self.vmtype, 'jobId': self.jobId, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'result': self.result}
        return s
    
    def __repr__(self):
        return "ip: "+str(self.ip)+" vmtype: "+str(self.vmtype)+" jobId: "+str(self.jobId)+" paraSigma: "+str(self.paraSigma)+" paraEA: "+str(self.paraEA)+" result: "+str(self.result)
    