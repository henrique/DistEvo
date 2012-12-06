import httplib
import json
import random
from vm import *
from job import *

####################################################################
# Clean DB first and EXECUTE testPut() before this script!!
#####################################################################

#url = 'jcluster12.appspot.com'
url = 'localhost:8080'

# GET single job 
connection =  httplib.HTTPConnection(url)
connection.request('GET', '/get/job/')
result = connection.getresponse()
data = result.read()

jobReal = None
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
            jobReal = job
else:
    print "ERROR http status = "+str(result.status)
connection.close()


# PUT job.running = True
job.running = True
l = { 'jobs': [ job.getJSON() ]}

data_string_jobs = json.dumps(l, indent=2)

# HTTP PUT Job
connection =  httplib.HTTPConnection(url)
body_content = data_string_jobs
headers = {"User-Agent": "python-httplib"}
connection.request('PUT', '/put/job/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT job.running = true OK - HTTP 200'
else:
    print 'error put job.running = true, http = '+str(result.status)
connection.close()

# PUT job.running = False, Finished=True, result=8.8

job.running = False
job.finished = True
job.result = 8.8
l = { 'jobs': [ job.getJSON() ]}

data_string_jobs = json.dumps(l, indent=2)

# HTTP PUT Job
connection =  httplib.HTTPConnection(url)
body_content = data_string_jobs
headers = {"User-Agent": "python-httplib"}
connection.request('PUT', '/put/job/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT job.finished=true etc. OK - HTTP 200'
else:
    print 'error put job.finished=True, http = '+str(result.status)
connection.close()

