#! /usr/bin/env python

import os
import sys
import logging
import shutil
import subprocess
import httplib
import json
import socket

from subprocess import call

PENALTY_VALUE=10000


#### URL #############

url = 'lsci-12.appspot.com'
#url = 'jcluster12.appspot.com'
#url = 'localhost:8080'

print 'Running on', url



class Job():
    def __init__(self, **entries):
        self.jobId = 0
        self.vmIp = None
        self.paraSigma = 0
        self.paraEA = 0
        self.running = False
        self.finished = False
        self.result = None
        self.counter = 0
        self.iteration = 0
        self.__dict__.update(entries)

    @staticmethod
    def serialize(obj):
        return obj.__dict__
        
    def __repr__(self):
        return str(self.__dict__)
        
        
class VM(dict):
    def __init__(self, **entries): 
        self.ip = ''
        self.vmtype = ''
        self.dateUpdate = ''
        self.__dict__.update(entries)
    
    @staticmethod
    def serialize(obj):
        return obj.__dict__
        
    def __repr__(self):
        return str(self.__dict__)



class LocalState():
    state = {} #TODO: persist state on db 
    
    @staticmethod
    def save(key, obj):
#        print "Saving", obj.__dict__
#        with open(key + '.bak', 'w') as f:
#            data = json.dumps(obj.__dict__, indent=2)
        LocalState.state = obj.__dict__
            
    @staticmethod
    def load(key, obj):
#        with open(key + '.bak', 'r') as f:
#            data = f.read_all()
#            data = json.loads(data)
            data = LocalState.state
#            print "Loading", data
            obj.__dict__.update(data)
            return obj



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


def pop2Jobs(opt):
    jobs = []
    i = 0
    for ex, sig in opt.new_pop:
        i += 1
        job = Job(jobId=i, paraEA=ex, paraSigma=sig, iteration=opt.cur_iter+1)
        jobs.append(job)
    return jobs


def getJobs():
    # GET  jobs
    jobs = []
    try:
        connection =  httplib.HTTPConnection(url)
        connection.request('GET', '/get/jobs/')
        result = connection.getresponse()
        data = result.read()
        
        if result.status == 200:
            decoded = json.loads(data)
            if decoded.has_key('jobs'): 
                count_jobs = len(decoded['jobs'])
                print 'count jobs: '+str(count_jobs)
                for job in decoded['jobs']:
                    temp = Job(**job)
                    jobs.append(temp)
#                    print job
        else:
            print "ERROR http status = "+str(result.status)
            
        connection.close()
    except:
        pass
    return jobs
    
    
def getNextJob():
    # GET single job
    job = None
    try:
        connection =  httplib.HTTPConnection(url)
        connection.request('GET', '/get/job/')
        result = connection.getresponse()
        data = result.read()
        
        if result.status == 200:
            decoded = json.loads(data)
            if decoded.has_key('jobs'): 
                count_jobs = len(decoded['jobs'])
                print 'count jobs: '+str(count_jobs)
                for j in decoded['jobs']:
                    job = Job(**j)
#                    print job
                    break
        else:
            print "ERROR http status = "+str(result.status)
            
        connection.close()
    except:
        pass
    return job
    
    
def getVMs():
    vms = []
    try:
        connection =  httplib.HTTPConnection(url)
        connection.request('GET', '/get/vms/')
        result = connection.getresponse()
        data = result.read()
        
        if result.status == 200:
            decoded = json.loads(data)
            if decoded.has_key('vms'): 
                count_vms = len(decoded['vms'])
                print 'count vms: '+str(count_vms)
                for vm in decoded['vms']:
                    temp = VM(**vm)
                    vms.append(temp)
#                    print vm
        else:
            print "ERROR http status = "+str(result.status)
            
        connection.close()
    except:
        pass
    return vms


def putJobs(jobs):
    # HTTP PUT Job's
    try:
        connection =  httplib.HTTPConnection(url)
        body_content = json.dumps({ 'jobs': jobs}, indent=2, default=Job.serialize)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/jobs/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT jobs OK - HTTP 200'
        else:
            print result.status
        connection.close()
    except:
        pass


def putJob(job):
    # HTTP PUT Job
    try:
        connection =  httplib.HTTPConnection(url)
        body_content = json.dumps({ 'jobs': [job] }, indent=2, default=Job.serialize)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/job/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT jobs OK - HTTP 200'
        else:
            print result.status
        connection.close()
    except:
        pass


def putVMs(vms):
    # HTTP PUT VM's
    try:
        connection =  httplib.HTTPConnection(url)
        body_content = json.dumps({ 'vms': vms}, indent=2)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/vms/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT vms OK - HTTP 200'
        else:
            print result.status
        connection.close()
    except:
        pass

def createVMs(popSize):
    return True #TODO


if __name__ == '__main__':
    #testing
    getJobs()
    getVMs()
    putJobs([
        Job(**{'paraSigma': 0.00203506248812, 'finished': False, 'paraEA': 0.826794792732, 'jobId': 1, 'running': False, 'result': None, 'vmIp': None}),
        Job(**{'paraSigma': 0.00203506248812, 'finished': False, 'paraEA': 0.826794792732, 'jobId': 2, 'running': False, 'result': None, 'vmIp': None})
        ])
    getJobs()
    putJobs([
        Job(**{'paraSigma': 0.00203506248812, 'finished': False, 'paraEA': 0.826794792732, 'jobId': 1, 'iter': 1, 'running': False, 'result': None, 'vmIp': None}),
        Job(**{'paraSigma': 0.00203506248812, 'finished': False, 'paraEA': 0.826794792732, 'jobId': 2, 'iter': 1, 'result': None, 'vmIp': None})
        ])
    getJobs()
    putJob(
        Job(**{'paraSigma': 0.00203506248812, 'finished': False, 'paraEA': 0.826794792732, 'jobId': 1, 'running': True, 'result': None, 'vmIp': 'LOCALHOST'})
        )
    getJobs()
    getJobs()
