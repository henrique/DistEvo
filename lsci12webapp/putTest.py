import httplib
import json
from vm import *

# Prepare PUT
ip = "129.12.34.23"
vmtype = "Amazon"
paraSigma = 0.345
paraEA = 9.3943
result = 0.34

x = VM(ip, vmtype, paraSigma, paraEA, result)
y = VM(ip, vmtype, paraSigma, paraEA, result)
x.result = result
y.result = 9.999

l = {'vms': [x.getJSON(), y.getJSON()]}

data_string = json.dumps(l, indent=2)

# HTTP PUT
url_local = 'localhost:8081'
url_gae = 'jcluster12.appspot.com'
connection =  httplib.HTTPConnection(url_local)
body_content = data_string
connection.request('PUT', '/put/', body_content)
result = connection.getresponse()
# Now result.status and result.reason contains interesting stuff
if result.status == 200:
    print 'OK'