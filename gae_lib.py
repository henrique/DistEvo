#! /usr/bin/env python

import httplib
import json
import sys

from subprocess import call


from gae_config import *
import numpy as np

PENALTY_VALUE = sys.float_info.max



class Job():
    def __init__(self, **entries):
        self.jobId = 0
        self.iteration = 0
        self.vmIp = None
        self.params = []
        self.result = None
        self.finished = False
        self.sent = 0
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





def pop2Jobs(opt):
    jobs = []
    i = 0
    for params in opt.new_pop:
        i += 1
        job = Job(jobId=i, params=params.tolist(), iteration=opt.cur_iter+1)
        jobs.append(job)
    return jobs


def restoreCurrentPop(popHolder, cur_iter, throw=False):
    """ GET current working population """
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
        connection.request('GET', '/get/pop/')
        result = connection.getresponse()
        data = result.read()
        
        if result.status == 200:
            decoded = json.loads(data)
            print 'Received working population: %d' % len(decoded['pop'])
            popHolder.pop  = np.array(decoded['pop'])
            popHolder.vals = np.array(decoded['vals'])
            popHolder.cur_iter = cur_iter
            
            #set best individual
            best_ix = np.argmin(popHolder.vals)
            popHolder.best_x = popHolder.pop[best_ix, :].copy()
            popHolder.best_y = popHolder.vals[best_ix].copy()
            return True
        else:
            raise Exception("ERROR http status = "+str(result.status))
            
    except Exception as ex:
        if throw:
            raise ex
        else:
            print ex
    finally:
        connection.close()
    return False
        
def putPop(opt):
    """ Update current working population """
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
        body_content = json.dumps({
                            'pop': opt.pop.tolist(),
                            'vals': opt.vals.tolist()
                        }, indent=2)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/pop/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT pop OK - HTTP 200'
            return True
        else:
            print result.status
    except Exception as ex:
        print ex
    finally:
        connection.close()
    return False


def getJobs(throw=False):
    # GET  jobs
    jobs = []
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
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
            raise Exception("ERROR http status = "+str(result.status))
            
    except Exception as ex:
        if throw:
            raise ex
        else:
            print ex
    finally:
        connection.close()
    return jobs
    
    
def getNextJob():
    # GET single job
    job = None
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
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
            
    except Exception as ex:
        print ex
    finally:
        connection.close()
    return job
    
    
def getVMs():
    vms = []
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
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
            
    except Exception as ex:
        print ex
    finally:
        connection.close()
    return vms


def putJobs(jobs):
    # HTTP PUT Job's
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
        body_content = json.dumps({ 'jobs': jobs}, indent=2, default=Job.serialize)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/jobs/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT jobs OK - HTTP 200'
            return True
        else:
            print result.status
    except:
        pass
    finally:
        connection.close()
    return False


def putJob(job):
    # HTTP PUT Job
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
        body_content = json.dumps({ 'jobs': [job] }, indent=2, default=Job.serialize)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/job/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT jobs OK - HTTP 200'
            return True
        else:
            print result.status
    except:
        pass
    finally:
        connection.close()
    return False


def putVMs(vms):
    # HTTP PUT VM's
    try:
        connection =  httplib.HTTPConnection(gae_config.getServerURL())
        body_content = json.dumps({ 'vms': vms}, indent=2)
        headers = {"User-Agent": "python-httplib"}
        connection.request('PUT', '/put/vms/', body_content, headers)
        result = connection.getresponse()
        if result.status == 200:
            print 'PUT vms OK - HTTP 200'
            return True
        else:
            print result.status
    except:
        pass
    finally:
        connection.close()
    return False

def createVMs(popSize):
    return True #TODO


if __name__ == '__main__':
    #testing
    getJobs()
    getVMs()
    assert putJobs([
        Job(**{'params': np.random.random_sample(2).tolist(), 'finished': False, 'jobId': 1, 'running': False, 'result': None, 'vmIp': None}),
        Job(**{'params': np.random.random_sample(2).tolist(), 'finished': False, 'jobId': 2, 'running': False, 'result': None, 'vmIp': None})
        ])
    getJobs()
    assert putJobs([
        Job(**{'params': np.random.random_sample(2).tolist(), 'finished': False, 'jobId': 1, 'iter': 1, 'running': False, 'result': None, 'vmIp': None}),
        Job(**{'params': np.random.random_sample(2).tolist(), 'finished': False, 'jobId': 2, 'iter': 1, 'result': None, 'vmIp': None})
        ])
    getJobs()
    assert putJob(
        Job(**{'params': np.random.random_sample(2).tolist(), 'finished': False, 'jobId': 1, 'running': True, 'result': None, 'vmIp': 'LOCALHOST'})
        )
    getJobs()
