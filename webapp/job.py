from google.appengine.ext import db
import time, logging

currentIteration = db.Model(key_name='curr')

class Job(db.Model):
    _redundancyLevel = 1
    _redundancyTimer = None
    _redundancyTimeout = 900 #15min
    
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
    @db.transactional(xg=True)
    def getNext():
        """ GET a not running, not finished, and not yet requested job from DB """
        q = Job.all().ancestor(currentIteration)
        q.filter("running =", False)
        q.filter("finished =", False)
        q.filter("counter <", Job._redundancyLevel) #redundancy level
        q.order("counter")
        job = q.get()
        
        if job is not None:
            # increment job counter
            job.counter += 1
            job.put()
            Job._redundancyLevel = job.counter #reset
        else:
            if Job._redundancyTimer is None:
                Job._redundancyTimer = time.time()
            elif time.time() - Job._redundancyTimer > Job._redundancyTimeout:
                Job._redundancyTimer = None
                Job._redundancyLevel += 1
                logging.info('New job redundancy level: %d', Job._redundancyLevel)
            
        return job

