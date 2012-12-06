import httplib
import json
from vm import *
from job import *


#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'localhost:8080'


# GET single vm test
connection =  httplib.HTTPConnection(url)
connection.request('GET', '/get/vms/')
result = connection.getresponse()
data = result.read()

if result.status == 200:
    decoded = json.loads(data)
    if decoded.has_key('vms'): 
        count_vms = len(decoded['vms'])
        print 'count vms: '+str(count_vms)
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
            print vm
else:
    print "ERROR http status = "+str(result.status)
connection.close()