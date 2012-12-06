import httplib
import json
from vm import *
from job import *

#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'localhost:8080'


# 3 Jobs as test for PUT
job1 = Job()
job2 = Job()
job3 = Job()
job1.jobId = 1
job2.jobId = 2
job3.jobId = 3
job1.paraSigma = 0.4534
job2.paraSigma = 0.43234
job3.paraSigma = 0.451134
job1.paraEA = 0.8877
job2.paraEA = 0.8811
job3.paraEA = 0.8872

# 3 VM's as test for PUT 
x = VM()
y = VM()
z = VM()
x.ip = '198.168.5.4'
x.vmtype = 'Amazon'
x.jobId = job1.jobId
x.paraSigma = job1.paraSigma
x.paraEA = job1.paraEA
y.ip = '192.168.1.1'
y.vmtype = 'FutureGrid'
y.jobId = job2.jobId
y.paraSigma = job2.paraSigma
y.paraEA = job2.paraEA
z.ip = '192.168.1.98'
z.vmtype = 'Amazon'
z.jobId = job3.jobId
z.paraSigma = job3.paraSigma
z.paraEA = job3.paraEA

l = { 'jobs': [job1.getJSON(), job2.getJSON(), job3.getJSON()]}
l2 = {'vms': [x.getJSON(), y.getJSON(), z.getJSON()]}

data_string_jobs = json.dumps(l, indent=2)
data_string_vms = json.dumps(l2, indent=2)

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