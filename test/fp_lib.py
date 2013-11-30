#! /usr/bin/env python

import os
import sys
import logging
import shutil
import subprocess
import httplib
import json

import numpy as np

from subprocess import call

PENALTY_VALUE=10000


#### URL #############
# localhost:8080
# jcluster12.appspot.com
######################
url = 'jcluster12.appspot.com'


class Job():
    def __init__(self, **entries):
        self.jobId = 0
        self.vmIp = None
        self.paraSigma = 0
        self.paraEA = 0
        self.running = False
        self.finished = False
        self.result = None
        self.__dict__.update(entries)
    
#    jobId = db.IntegerProperty()
#    vmIp = db.StringProperty()
#    paraSigma = db.FloatProperty()
#    paraEA = db.FloatProperty()
#    result = db.FloatProperty()
#    running = db.BooleanProperty()
#    finished = db.BooleanProperty()

    @staticmethod
    def serialize(obj):
        return obj.__dict__
        
    def __repr__(self):
        return str(self.__dict__)
 
#    def set(self, job):
#        self.jobId = job['jobId']
#        self.vmIp = job['vmIp']
#        self.paraSigma = job['paraSigma']
#        self.paraEA = job['paraEA']
#        self.running = job['running']
#        self.finished = job['finished']
#        self.result = job['result']
        
        
        
class VM(dict):
    def __init__(self, **entries): 
        self.__dict__.update(entries)
    
#    ip = db.StringProperty()
#    vmtype = db.StringProperty()
#    dateUpdate = db.DateTimeProperty(auto_now_add=True)
    
    @staticmethod
    def serialize(obj):
        return obj.__dict__
        
    def __repr__(self):
        return str(self.__dict__)
    
#    def set(self, vm):
#        self.ip = vm['ip']
#        self.vmtype = vm['vmtype']



class nlcOne4eachPair():
  def __init__(self, lower_bds, upper_bds):

    self.lower_bds = lower_bds
    self.upper_bds = upper_bds
    self.ctryPair = ['JP', 'US']
 
    self.EY = [ 1.005416, 1.007292 ]
    self.sigmaY = [ 0.010643, 0.00862 ]
      
  def __call__(self, x):
    '''
    Evaluates constraints. 
    Inputs: 
      x -- Habit parametrization, EH, sigmaH
    Outputs: 
      c -- Vector of constraints values, where c_i >= 0 indicates that constraint is satisified.
           Constraints 1-4 are bound constraints for EH and sigmaH
           Constraints 5 and 6 are economic constraints, one for Japan, one for US. 
    '''
    c = np.array([])
    # bound constraints
    # EH box
    c = np.append(c, x[0] - self.lower_bds[0])
    c = np.append(c, -(x[0] - self.upper_bds[0]))
    # sigmaH box
    c = np.append(c, x[1] - self.lower_bds[1])
    c = np.append(c, -(x[1] - self.upper_bds[1]))
    # both countries have the same E
    EH     = np.array([x[0], x[0]])
    sigmaH = np.array([x[1], x[1]])

    for ixCtry in range(2):
      c = np.append(c, ( EH[ixCtry] / sigmaH[ixCtry] ) * ( self.sigmaY[ixCtry] / self.EY[ixCtry] ) - 1 )

    return c

def runApp(ex, sigmax):
      print "forwardPremiumOut running with EX=%g, sigmaX=%g ..." % (ex, sigmax)
      # the actual vale should be extracted from the forwardPremium output file 'simulation.out'
      call(["rm", "-rf", "output*", "parameters.in"])
      #call(["mkdir", "output"])
      rf = open('parameters.in.orig', 'r')
      with open('parameters.in', 'w') as wf:
        while 1:
          line = rf.readline()
          if not line:
              break
          line = line.replace('EX', str(ex))
          line = line.replace("sigmaX", str(sigmax))
          wf.write(line)
      call(["./forwardPremiumOut"])
      try:
        with open('output/simulation.out') as of:
          print "simulation.out", of.readline() #TODO: read result
          FAKE_FF_BETA = 2
          return FAKE_FF_BETA
      except IOError as e:
        print 'Job Failed!'
        
      return PENALTY_VALUE


def getJobs():
    # GET  jobs
    connection =  httplib.HTTPConnection(url)
    connection.request('GET', '/get/jobs/')
    result = connection.getresponse()
    data = result.read()
    jobs = []
    
    if result.status == 200:
        decoded = json.loads(data)
        if decoded.has_key('jobs'): 
            count_jobs = len(decoded['jobs'])
            print 'count jobs: '+str(count_jobs)
            for job in decoded['jobs']:
                temp = Job(**job)
                jobs.append(temp)
                print job
    else:
        print "ERROR http status = "+str(result.status)
        
    connection.close()
    return jobs
    
    
def getNextJob():
    # GET single job
    connection =  httplib.HTTPConnection(url)
    connection.request('GET', '/get/job/')
    result = connection.getresponse()
    data = result.read()
    job = None
    
    if result.status == 200:
        decoded = json.loads(data)
        if decoded.has_key('jobs'): 
            count_jobs = len(decoded['jobs'])
            print 'count jobs: '+str(count_jobs)
            for j in decoded['jobs']:
                job = Job(**j)
                print job
                break
    else:
        print "ERROR http status = "+str(result.status)
        
    connection.close()
    return job
    
    
def getVMs():
    connection =  httplib.HTTPConnection(url)
    connection.request('GET', '/get/vms/')
    result = connection.getresponse()
    data = result.read()
    vms = []
    
    if result.status == 200:
        decoded = json.loads(data)
        if decoded.has_key('vms'): 
            count_vms = len(decoded['vms'])
            print 'count vms: '+str(count_vms)
            for vm in decoded['vms']:
                temp = VM(**vm)
                vms.append(temp)
                print vm
    else:
        print "ERROR http status = "+str(result.status)
        
    connection.close()
    return vms


def putJobs(jobs):
    # HTTP PUT Job's
    connection =  httplib.HTTPConnection(url)
    body_content = json.dumps({ 'jobs': jobs}, indent=2, default=Job.serialize)
    print body_content
    headers = {"User-Agent": "python-httplib"}
    connection.request('PUT', '/put/', body_content, headers)
    result = connection.getresponse()
    if result.status == 200:
        print 'PUT jobs OK - HTTP 200'
    else:
        print result.status
    connection.close()

def putVMs(vms):
    # HTTP PUT VM's
    connection =  httplib.HTTPConnection(url)
    body_content = json.dumps({ 'vms': vms}, indent=2, default=VM.serialize)
    print body_content
    headers = {"User-Agent": "python-httplib"}
    connection.request('PUT', '/put/', body_content, headers)
    result = connection.getresponse()
    if result.status == 200:
        print 'PUT vms OK - HTTP 200'
    else:
        print result.status
    connection.close()
