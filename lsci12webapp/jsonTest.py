#!/usr/bin/env python2.7

import json
from vm import *

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
print 'ENCODED:', data_string

text_file = open("JSON.txt", "w")
text_file.write(data_string)
text_file.close()

text_file2 = open("JSON.txt", "r")
data_string2 = text_file2.read()
text_file2.close()

decoded = json.loads(data_string2)
decoded2 = json.dumps(decoded, indent=2)

print decoded
print 'DECODED:', decoded2

count_vms = len(decoded['vms'])
vms = []

for vm in decoded['vms']:
    ip = vm['ip']
    vmtype = vm['vmtype']
    paraSigma = vm['paraSigma']
    paraEA = vm['paraEA']
    result = vm['result']
    vms.append( VM(ip, vmtype, paraSigma, paraEA, result) )
    
print "Count VM's:", count_vms
for vm in vms:
    print vm
    