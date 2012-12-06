import httplib
import json
from vm import *
from job import *


#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'localhost:8080'


# GET single job test
connection =  httplib.HTTPConnection(url)
connection.request('GET', '/get/job/')
result = connection.getresponse()
data = result.read()

if result.status == 200:
    decoded = json.loads(data)
    if decoded.has_key('jobs'): 
        count_jobs = len(decoded['jobs'])
        print 'count jobs: '+str(count_jobs)
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
            print job
else:
    print "ERROR http status = "+str(result.status)
connection.close()