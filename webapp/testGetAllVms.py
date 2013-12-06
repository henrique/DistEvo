import httplib
import json
from vm import *
from job import *


#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'jcluster12.appspot.com'


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
            temp = VM(key_name=vm['ip'])
            temp.set(vm)
            vms.append(temp)
        
        for vm in vms:
            print vm
else:
    print "ERROR http status = "+str(result.status)
connection.close()
