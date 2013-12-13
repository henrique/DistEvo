import httplib
import json
import random

from dispatcher import Job

N_JOBS = 10

from config import *
url = server_target

jobs = []
for i in range(N_JOBS):
    job = Job()
    job.jobId = i
    job.paraEA = random.uniform(0.5, 1.0)
    job.paraSigma = random.uniform(0.001, 0.01)
    job.running = False
    job.finished = False
    jobs.append(job)

l = { 'jobs': [ job.getJSON() for job in jobs ]}

# HTTP PUT Job's
connection =  httplib.HTTPConnection(url)
headers = {"User-Agent": "python-httplib"}
connection.request('PUT', '/put/', json.dumps(l, indent=2), headers)
result = connection.getresponse()
if result.status == 200:
    print 'PUT jobs OK - HTTP 200'
else:
    print result.status
connection.close()
