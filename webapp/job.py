from google.appengine.ext import db
from google.appengine.api import memcache as mc
import os, time, logging

currentIteration = db.Model(key_name='curr')

def isLocal():
    return os.environ["SERVER_NAME"] == "localhost"

class Archive(db.Model):
    jobs = db.TextProperty()
    pop  = db.TextProperty()
    vals = db.TextProperty()

class Pop(db.Model):
    """ Current population """
    pop  = db.TextProperty()
    vals = db.TextProperty()

class Job(db.Model):
    _redundancyTimeout = 5 if isLocal() else 900 #15min
    
    jobId = db.IntegerProperty()
    iteration = db.IntegerProperty()
    vmIp = db.StringProperty(indexed=False)
    params = db.ListProperty(float, indexed=False)
    result = db.FloatProperty(indexed=False)
    finished = db.BooleanProperty()
    sent = db.IntegerProperty(required=True, default=0)
    

    def getJSON(self):
        s = {'jobId': self.jobId, 'iteration': self.iteration, 'vmIp': self.vmIp, 'params': self.params, 'finished': self.finished, 'result': self.result, 'sent': self.sent}
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
        self.finished = job['finished']
        self.result = job['result']
        self.sent = job['sent']


    @staticmethod
    def currentIteration():
        for it in db.GqlQuery("SELECT iteration FROM Job ORDER BY iteration DESC").fetch(1):
            return it
        
        return -1


    @staticmethod
    def getRedundancyLevel():
        level = mc.get('_redundancyLevel')
        if level is None: level = 1;
        return level
    
    @staticmethod
    def setRedundancyLevel(redundancyLevel):
        return mc.set('_redundancyLevel', redundancyLevel, 7200) #2h
    
    @staticmethod
    def getRedundancyTimer():
        return mc.get('_redundancyTimer')
    
    @staticmethod
    def setRedundancyTimer(redundancyTimer):
        return mc.set('_redundancyTimer', redundancyTimer, 7200) #2h
    
    @staticmethod
    def incrRedundancyTimer():
        #mc.incr('_redundancyLevel')
        Job.setRedundancyLevel(Job.getRedundancyLevel() + 1)
        logging.info('New job redundancy level: %d', Job.getRedundancyLevel())


    @staticmethod
    @db.transactional(xg=True)
    def getNext():
        """ GET a not running, not finished, and not yet requested job from DB """
        redundancyLevel = Job.getRedundancyLevel()
        
        q = Job.all().ancestor(currentIteration)
        q.filter("finished =", False)
        q.filter("sent <", redundancyLevel) #redundancy level
        q.order("sent")
        job = q.get()
        
        if job is not None:
            # increment job counter
            job.sent += 1
            job.put()
            Job.setRedundancyLevel( job.sent ) #reset
        else:
            redundancyTimer = Job.getRedundancyTimer()
            logging.info('No new Job: redundancyLevel:%d redundancyTimer:%f', redundancyLevel, time.time() - (redundancyTimer or 0))
            if redundancyTimer is None:
                Job.setRedundancyTimer( time.time() )
            elif time.time() - redundancyTimer > Job._redundancyTimeout:
                Job.setRedundancyTimer(None)
                Job.incrRedundancyTimer()
            
        return job


    @staticmethod
    def getAll(): #cur_iter):
        """ GET all jobs from DB """
        jobs = db.GqlQuery("Select * "
                           "FROM Job "
                           "ORDER BY iteration, jobId")
                           #"WHERE iteration = :1 "#, cur_iter)
        return jobs
