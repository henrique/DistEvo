import httplib
import json
import random
from vm import *
from job import *

N_JOBS = 10

#url = 'jcluster12.appspot.com'
url = 'localhost:8080'

# JOBS
jobs = []
for i in range(N_JOBS):
    job = Job()
    job.jobId = i
    job.paraEA = random.uniform(0.5, 1.0)
    job.paraSigma = random.uniform(0.001, 0.01)
    job.running = False
    job.finished = False
    jobs.append(job)

# 1 VM, because you can not add 2 VM's from the same machine (Ip == key for datastore)
x = VM()
x.vmtype = 'Amazon'

l = { 'jobs': [ job.getJSON() for job in jobs ]}
l2 = {'vms': [ x.getJSON() ]}

data_string_jobs = json.dumps(l, indent=2)
data_string_vms = json.dumps(l2, indent=2)

file = open('files/jsonJobs.txt', 'w')
file.write(data_string_jobs)
file.close()

file = open('files/jsonVms.txt', 'w')
file.write(data_string_vms)
file.close()

# HTTP PUT Job's
connection =  httplib.HTTPConnection(url)
body_content = data_string_jobs
headers = {"User-Agent": "python-httplib"}
connection.request('PUT', '/put/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT jobs OK - HTTP 200'
else:
    print result.status
connection.close()

# HTTP PUT VM's
connection =  httplib.HTTPConnection(url)
body_content = data_string_vms
connection.request('PUT', '/put/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT vms OK - HTTP 200'
else:
    print result.status
connection.close()

