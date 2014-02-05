import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache

import logging
import json
import time
from vm import VM
from job import Job, Archive, Pop, isLocal, currentIteration
from stats import ShowStats


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        file = open('index.html')
        self.response.out.write(file.read())


class GetJob(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get single job received")
        
        # GET a not running& not finished& not requested job from DB
        job = Job.getNext()
        if job is None:
            logging.info('no not-running job found that was not requested already, abort')
            self.error(204)
            return
        
        l = { 'jobs': [job.getJSON()]}
        content = json.dumps(l, indent=2)
        logging.info(job)
        self.response.out.write(content)


class GetVm(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get single vm received")
        
        # GET VM with same request.remote_addr
        q = VM.all()
        q.filter("ip =", self.request.remote_addr)

        vm = q.get()
        if vm == None:
            logging.info('no vm found for this ip: '+str(self.request.remote_addr)+', abort')
            self.error(204)
            return
        
        l = { 'vms': [vm.getJSON()]}
        content = json.dumps(l, indent=2)
        # logging.info(content)
        self.response.out.write(content)
       
        
class GetAllJobs(webapp2.RequestHandler):
    cachekey = 'alljobs'
    cacheTimeout = 1 if isLocal() else 600 #10min

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        data = GetAllJobs.load()
#         logging.info(data)
        self.response.out.write(data)
    
    
    @staticmethod
    def load(cache=True):
        data = memcache.get(GetAllJobs.cachekey)
        if data is None:
            data = GetAllJobs.getFromDB()
            if cache and memcache.set(GetAllJobs.cachekey, data, GetAllJobs.cacheTimeout):
                logging.info("Adding jobs to cache: " + GetAllJobs.cachekey)
        return data
    
    
    @staticmethod
    def getFromDB():
        #l = {}
        #cur_iter = Job.currentIteration()
        logging.info("Get all jobs from db")
        #l['iteration'] = cur_iter
        
        jobs = Job.getAll()
        return Job.dump(jobs)


class GetAllVms(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get all vms received")
        
        vms = db.GqlQuery("Select * "
                           "FROM VM "
                           "ORDER BY ip")
        countVms = vms.count()
        logging.info("countVms: "+str(countVms))
        if countVms > 0:
           l = { 'vms': [vm.getJSON() for vm in vms]}
        else:
           l = { 'vms': []}
          
        content = json.dumps(l, indent=2)
        logging.info(content)
        self.response.out.write(content)


class GetPopulation(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get population received")
        
        pop = Pop.all().get()
        
        if pop is not None:
            content = json.dumps({
                                'pop': json.loads(pop.pop),
                                'vals': json.loads(pop.vals)
                            }, indent=2)
            logging.info(content)
            self.response.out.write(content)
        else:
            self.error(204)
            

class PutPopulation(webapp2.RequestHandler):
    def put(self):
        logging.info('put Population received')
        data_string = self.request.body
        logging.info(data_string)
        decoded = json.loads(data_string)
        
        pop = Pop(key_name='curr')
        pop.pop  = json.dumps(decoded['pop'])
        pop.vals = json.dumps(decoded['vals'])
        pop.put()


class PutAllJobs(webapp2.RequestHandler):
    _lockKey = '_job_lock'
    
    def put(self):
        logging.info('put all jobs received')
        
        if memcache.get(PutAllJobs._lockKey) is not None:
            logging.warn('jobs locked by another caller')
            self.error(204)
            return
        else:
            memcache.set(PutAllJobs._lockKey, True, 5) #5s
        
        data_string = self.request.body
        decoded = json.loads(data_string)
        logging.info(json.dumps(decoded, indent=2))
        
        if decoded.has_key('jobs'):
            jobs = decoded['jobs']
            logging.info('count jobs: ' + str(len(jobs)))
            
            data = Job.getAll()
            if data is not None:
                if data.count(1) > 0:
                    arch = Archive(key_name=str(data[0].iteration))
                    arch.jobs = Job.dump(data)
                    pop = Pop.all().get() #get current population to archive
                    if pop is not None:
                        arch.pop = pop.pop
                        arch.vals = pop.vals
                    arch.put()
            
            Job.putAll(jobs)
            memcache.delete(GetAllJobs.cachekey)
            memcache.delete(PutAllJobs._lockKey)
            
            email = self.request.get("email")
            if email:
                logging.info(email)
                from google.appengine.api import mail
                mail.send_mail(sender=email, to=email, subject="New iteration started", body=data_string)
            
                
      
      
class PutAllVms(webapp2.RequestHandler):
  def put(self):
   
    logging.info('put all vms received')
   
    data_string = self.request.body
    decoded = json.loads(data_string)
    decoded2 = json.dumps(decoded, indent=2)
    
    logging.info(decoded2)
   
    if decoded.has_key('vms'):
        count_vms = len(decoded['vms'])
        logging.info('count vms: '+str(count_vms))
        vms = []
        for vm in decoded['vms']:
            temp = VM(key_name=vm['ip'])
            temp.set(vm)
            temp.ip = vm['ip']
            vms.append(temp)
        
        for vm in vms:
            vm.put()
            logging.info('put vm['+vm.ip+'] into datastore')
    
    else:
        logging.info('no key vms defined')
        self.error(500)
        return
        


class PutJob(webapp2.RequestHandler):
  def put(self):
    logging.info('put single job received')
    data_string = self.request.body
    logging.info(data_string)
    decoded = json.loads(data_string)
    if decoded.has_key('jobs'): 
        count_jobs = len(decoded['jobs'])
        if count_jobs > 1:
            logging.info("more than 1 job, abort")
            self.error(204)
            return
        
        jobs = []
        for job in decoded['jobs']:
            temp = Job(key_name=str(job['jobId']), parent=currentIteration)
            temp.set(job)
            # Lookup Job in DB and see if already running
            # if not running overwrite and send 200 else 500
            q = Job.all()
            q.filter("jobId =", temp.jobId)
            result = q.get()
            if result is not None:
#                 if result.vmIp != self.request.remote_addr:
#                     logging.info('job already running from other vm, abort')
#                     self.error(500)
#                     return
                if result.finished:
                    continue #skip job
                if result.iteration != temp.iteration:
                    continue #skip job
                temp.vmIp = self.request.remote_addr
                jobs.append(temp)
            else:
                self.error(204)
                
        
        for job in jobs:
            job.put()
            logging.info('put job['+str(job.jobId)+'] into datastore')
            if job.finished:
                memcache.delete(GetAllJobs.cachekey)
                logging.info('memcache deleted!!!!')


class PutVm(webapp2.RequestHandler):
    def put(self):
        
        logging.info('put single vm received')
        
        data_string = self.request.body
        decoded = json.loads(data_string)
        decoded2 = json.dumps(decoded, indent=2)
        
        logging.info(decoded2)
       
        if decoded.has_key('vms'):
            count_vms = len(decoded['vms'])
            logging.info('count vms: '+str(count_vms))
            if count_vms > 1:
                logging.info("more than 1 vm, abort")
                self.error(500)
                return
            vms = []
            for vm in decoded['vms']:
                ip = self.request.remote_addr
                temp = VM(key_name=ip)
                temp.set(vm)
                temp.ip = ip
                vms.append(temp)
            
            for vm in vms:
                vm.put()
                logging.info('put vm['+vm.ip+'] into datastore')
        
        else:
            logging.info('no key vms defined')
            self.error(500)
            return                  

class bulkdelete(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM Job")
                if q.count() <= 0: break
                db.delete(q.fetch(200))
                time.sleep(0.2)
        except Exception, e:
            self.response.out.write(repr(e)+'\n')
            pass
        memcache.delete(GetAllJobs.cachekey)
        logging.info('memcache deleted!!!!')
        
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM VM")
                if q.count() <= 0: break
                db.delete(q.fetch(200))
                time.sleep(0.2)
        except Exception, e:
            self.response.out.write(repr(e)+'\n')
            pass
        
        self.response.out.write('Done!\n ' + time.strftime("%a, %d %b %Y %H:%M:%S +0000"))
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/put/jobs/', PutAllJobs),
                               ('/put/vms/', PutAllVms),
                               ('/put/job/', PutJob),
                               ('/put/vm/', PutVm),
                               ('/put/pop/', PutPopulation),
                               ('/get/job/', GetJob),
                               ('/get/vm/', GetVm),
                               ('/get/jobs/', GetAllJobs),
                               ('/get/vms/', GetAllVms),
                               ('/get/pop/', GetPopulation),
                               ('/stats', ShowStats),
                               ('/admin/i_really_want_to_delete_everything', bulkdelete)],
                              debug=True)

# APP STARTUP - INIT DB
logging.info('app startup')
