import httplib
import json
import numpy as np
from vm import VM
from job import Job

from gae_config import *
url = server_target

YOUR_IP = '127.0.0.1'

N_JOBS = 10


# JOBS
jobs = []
for i in range(N_JOBS):
    job = Job()
    job.jobId = i
    job.iteration = 1
    job.params = np.random.random_sample(2).tolist()
    job.finished = False
    jobs.append(job)

# 3 VM's
vms = []
x = VM()
y = VM()
z = VM()
x.vmtype = 'Test'
y.vmtype = 'Test'
z.vmtype = 'Test'
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

