from google.appengine.ext import db

class Job(db.Model):
    
    jobId = db.IntegerProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()

    def getJSON(self):
        s = {'jobId': self.jobId, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA}
        return s
    