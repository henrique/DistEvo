import httplib
import json
from vm import *
from job import *


#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'jcluster12.appspot.com'


# GET single job test
connection =  httplib.HTTPConnection(url)
connection.request('GET', '/get/jobs/')
result = connection.getresponse()
data = result.read()

if result.status == 200:
    decoded = json.loads(data)
    if decoded.has_key('jobs'): 
        count_jobs = len(decoded['jobs'])
        print 'count jobs: '+str(count_jobs)
        jobs = []
        for job in decoded['jobs']:
            temp = Job(key_name=str(job['jobId']))
            temp.set(job)
            jobs.append(temp)
        
        for job in jobs:
            print job
else:
    print "ERROR http status = "+str(result.status)
connection.close()