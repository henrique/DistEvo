import httplib
import json
from vm import *
from param import *

# Prepare PUT
ip = "129.12.34.23"
ip2 = "129.12.34.99"
vmtype = "Amazon"
paraSigma = 0.345
paraEA = 9.3943
result = 0.34

# 2 VM's as test for PUT with curl
x = VM()
y = VM()
x.ip = ip
x.vmtype = vmtype
x.paraSigma = paraSigma
x.paraEA = paraEA
x.result = result
y.ip = ip2
y.vmtype = vmtype
y.paraSigma = paraSigma
y.paraEA = paraEA
y.result = 9.999
# List of PARAM objects as json PUT with curl
z = Param()
z.index = 1
z.paraSigma = 378.3847322
z.paraEA = 384.203383499
q = Param()
q.index = 2
q.paraSigma = 8.00001
q.paraEA = 1.11111

l = {'vms': [x.getJSON(), y.getJSON()]}
l2 = { 'params': [z.getJSON(), q.getJSON()]}

data_string = json.dumps(l, indent=2)
data_string_param = json.dumps(l2, indent=2)

# HTTP PUT VM's
url_local = 'localhost:8080'
url_gae = 'jcluster12.appspot.com'
connection =  httplib.HTTPConnection(url_local)
body_content = data_string
connection.request('PUT', '/put/', body_content)
result = connection.getresponse()
# Now result.status and result.reason contains interesting stuff
if result.status == 200:
    print 'PUT vms OK - 200'
    
# HTTP PUT PARAM's
body_content = data_string_param
connection.request('PUT', '/put/', body_content)
result = connection.getresponse()
# Now result.status and result.reason contains interesting stuff
if result.status == 200:
    print 'PUT params OK - 200'
connection.close()