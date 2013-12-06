import httplib
import json
import random
from vm import *
from job import *

#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'localhost:8080'
YOUR_IP = '127.0.0.1'

N_JOBS = 10


# JOBS
jobs = []
for i in range(N_JOBS):
    job = Job()
    job.jobId = i
    job.iteration = 1
    job.paraEA = random.uniform(0.5, 1.0)
    job.paraSigma = random.uniform(0.001, 0.01)
    job.running = False
    job.finished = False
    jobs.append(job)

# 3 VM's
vms = []
x = VM()
y = VM()
z = VM()
x.vmtype = 'Amazon'
y.vmtype = 'Amazon'
z.vmtype = 'Amazon'
x.ip = '127.0.0.1'
y.ip = '192.168.2.2'
z.ip = '192.168.3.3'

vms.append(x)
vms.append(y)
vms.append(z)

l = { 'jobs': [ job.getJSON() for job in jobs ]}
l2 = {'vms': [ vm.getJSON() for vm in vms]}

data_string_jobs = json.dumps(l, indent=2)
data_string_vms = json.dumps(l2, indent=2)



# HTTP PUT Job's
connection =  httplib.HTTPConnection(url)
body_content = data_string_jobs
#print body_content
headers = {"User-Agent": "python-httplib"}
connection.request('PUT', '/put/jobs/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT jobs OK - HTTP 200'
else:
    print result.status
connection.close()

# HTTP PUT VM's
connection =  httplib.HTTPConnection(url)
body_content = data_string_vms
#print body_content
connection.request('PUT', '/put/vms/', body_content, headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT vms OK - HTTP 200'
else:
    print result.status
connection.close()

