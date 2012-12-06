from google.appengine.ext import db

class Job(db.Model):
    
    jobId = db.IntegerProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()
    running = db.BooleanProperty()

    def getJSON(self):
        s = {'jobId': self.jobId, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'running': self.running}
        return s
    
    def __repr__(self):
        return "jobId: "+str(self.jobId)+" paraSigma: "+str(self.paraSigma)+" paraEA:"+str(self.paraEA)+" running:"+str(self.running)
    