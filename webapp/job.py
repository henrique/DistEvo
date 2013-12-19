from google.appengine.ext import db
import json

class Job(db.Model):
    
    jobId = db.IntegerProperty()
    iteration = db.IntegerProperty()
    vmIp = db.StringProperty()
    params = db.ListProperty(float)
    result = db.FloatProperty()
    running = db.BooleanProperty()
    finished = db.BooleanProperty()
    counter = db.IntegerProperty(required=True, default=0)
    

    def getJSON(self):
        s = {'jobId': self.jobId, 'iteration': self.iteration, 'vmIp': self.vmIp, 'params': self.params, 'running': self.running, 'finished': self.finished, 'result': self.result, 'counter': self.counter}
        return s


    @staticmethod
    def serialize(obj):
        return obj.__dict__


    def __repr__(self):
        return str(self.getJSON())


    def set(self, job):
        self.jobId = job['jobId']
        self.iteration = job['iteration']
        self.vmIp = job['vmIp']
        self.params = job['params']
        self.running = job['running']
        self.finished = job['finished']
        self.result = job['result']
        self.counter = job['counter']


    @staticmethod
    def currentIteration():
        for it in db.GqlQuery("SELECT iteration FROM Job ORDER BY iteration DESC").fetch(1):
            return it
        
        return -1


    @staticmethod
    def getNext():
        """ GET a not running& not finished& not requested job from DB """
        q = Job.all()
        q.filter("running =", False)
        q.filter("finished =", False)
        q.filter("counter <", 2) #redundancy level
        q.order("counter")
        return q.get()

