import webapp2
import logging
import json
from google.appengine.ext import db
from vm import *
from job import *

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      file = open('index.html')
      self.response.out.write(file.read())

class GetJob(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get single job received")
        
        # GET a not running job from DB
        jobs = db.GqlQuery("Select * "
                           "FROM Job "
                           "ORDER BY jobId")
        countJobs = jobs.count()
        logging.info("countJobs: "+str(countJobs))
        if countJobs > 0:
           l = { 'jobs': [jobs[0].getJSON()]}
        else:
           l = { 'jobs': []}
          
        content = json.dumps(l, indent=2)
        logging.info(content)
        self.response.out.write(content)
        
class GetAllJobs(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        logging.info("get all jobs received")
        
        # GET a not running job from DB
        jobs = db.GqlQuery("Select * "
                           "FROM Job "
                           "ORDER BY jobId")
        countJobs = jobs.count()
        logging.info("countJobs: "+str(countJobs))
        if countJobs > 0:
           l = { 'jobs': [job.getJSON() for job in jobs]}
        else:
           l = { 'jobs': []}
          
        content = json.dumps(l, indent=2)
        logging.info(content)
        self.response.out.write(content)
      
      
class Put(webapp2.RequestHandler):
  def put(self):
   
    logging.info('put received')
   
    data_string = self.request.body
    decoded = json.loads(data_string)
    decoded2 = json.dumps(decoded, indent=2)
    
    logging.info(decoded2)
   
    if decoded.has_key('vms'):
        count_vms = len(decoded['vms'])
        logging.info('count vms: '+str(count_vms))
        vms = []
        for vm in decoded['vms']:
            ip = vm['ip']
            vmtype = vm['vmtype']
            jobId = vm['jobId']
            paraSigma = vm['paraSigma']
            paraEA = vm['paraEA']
            result = vm['result']
            temp = VM(key_name=ip)
            temp.ip = ip
            temp.vmtype = vmtype
            temp.jobId = jobId
            temp.paraSigma = paraSigma
            temp.paraEA = paraEA
            temp.result = result
            vms.append(temp)
        
        for vm in vms:
            vm.put()
            logging.info('put vm['+vm.ip+'] into datastore')
        
    if decoded.has_key('jobs'): 
        count_jobs = len(decoded['jobs'])
        logging.info('count jobs: '+str(count_jobs))
        jobs = []
        for job in decoded['jobs']:
            jobId = job['jobId']
            paraSigma = job['paraSigma']
            paraEA = job['paraEA']
            running = job['running']
            temp = Job(key_name=str(jobId))
            temp.jobId = jobId
            temp.paraSigma = paraSigma
            temp.paraEA = paraEA
            temp.running = running
            jobs.append(temp)
        
        for job in jobs:
            job.put()
            logging.info('put job['+str(job.jobId)+'] into datastore')
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/put/', Put),
                               ('/get/job/', GetJob),
                               ('/get/jobs/', GetAllJobs)],
                              debug=True)

# APP STARTUP - INIT DB
logging.info('app startup')
