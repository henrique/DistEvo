import webapp2
import logging
import json
from google.appengine.ext import db
from vm import *
from param import *

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Hello, webapp2 World!')
      
      
class Put(webapp2.RequestHandler):
  def put(self):
   
    logging.info('put received')
   
    data_string = self.request.body
    decoded = json.loads(data_string)
    decoded2 = json.dumps(decoded, indent=2)
#    logging.info(decoded2)
   
    if decoded.has_key('vms'):
        count_vms = len(decoded['vms'])
        logging.info('count vms: '+str(count_vms))
        vms = []
        for vm in decoded['vms']:
            ip = vm['ip']
            vmtype = vm['vmtype']
            paraSigma = vm['paraSigma']
            paraEA = vm['paraEA']
            result = vm['result']
            temp = VM(key_name=ip)
            temp.ip = ip
            temp.vmtype = vmtype
            temp.paraSigma = paraSigma
            temp.paraEA = paraEA
            temp.result = result
            vms.append(temp)
        
        for vm in vms:
            vm.put()
            logging.info('put vm['+vm.ip+'] into datastore')
        
    if decoded.has_key('params'): 
        count_params = len(decoded['params'])
        logging.info('count params: '+str(count_params))
        params = []
        for para in decoded['params']:
            index = para['index']
            paraSigma = para['paraSigma']
            paraEA = para['paraEA']
            temp = Param(key_name=str(index))
            temp.index = index
            temp.paraSigma = paraSigma
            temp.paraEA = paraEA
            params.append(temp)
        
        for para in params:
            para.put()
            logging.info('put param['+str(para.index)+'] into datastore')
        

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/put/', Put)],
                              debug=True)

# APP STARTUP - INIT DB
logging.info('app startup')
