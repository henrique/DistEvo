from google.appengine.ext import db

class Job(db.Model):
    
    jobId = db.IntegerProperty()
    paraSigma = db.FloatProperty()
    paraEA = db.FloatProperty()
    result = db.FloatProperty()
    running = db.BooleanProperty()
    finished = db.BooleanProperty()

    def getJSON(self):
        s = {'jobId': self.jobId, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'running': self.running, 'finished': self.finished, 'result': self.result}
        return s
    
    def __repr__(self):
        return "jobId: "+str(self.jobId)+" paraSigma: "+str(self.paraSigma)+" paraEA:"+str(self.paraEA)+" running: "+str(self.running)+" finished: "+str(self.finished)+" result: "+str(self.result)
    
    def set(self, job):
        self.jobId = job['jobId']
        self.paraSigma = job['paraSigma']
        self.paraEA = job['paraEA']
        self.running = job['running']
        self.finished = job['finished']
        self.result = job['result']