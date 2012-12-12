#!/usr/bin/env python

import os, sys
import datetime, time
import httplib, json
import multiprocessing
import shutil
import subprocess
import re
import random

# URL = 'localhost:8080'
# URL = 'jcluster12.appspot.com'
URL = 'lsci-2012.appspot.com'

SKEL_INPUT = '/home/henrique/lsci/project/lsci2012/test/input'
BIN_PATH = '/home/henrique/lsci/project/lsci2012/test'
BIN = 'forwardPremiumOut'
WORKDIR = '/var/run/lsci2012'
NCORES = multiprocessing.cpu_count()

PENALTY = 99.99

R_FAMA_FRENCH_BETA = re.compile(r"^FamaFrenchBeta:\s*(.*)$")

class Job():
    def __init__(self, key_name=None, json=None):
        self.key_name = key_name
        self.proc = None
        if json == None:
            self.jobId = 0
            self.iteration = 0
            self.vmIp = '0.0.0.0'
            self.paraSigma = None
            self.paraEA = None
            self.result = None
            self.running = False
            self.finished = False
            self.counter = 0
        else:
            self.set(json)


    def getJSON(self):
        s = {'jobId': self.jobId, 'iteration': self.iteration, 'vmIp': self.vmIp, 'paraSigma': self.paraSigma, 'paraEA': self.paraEA, 'running': self.running, 'finished': self.finished, 'result': self.result, 'counter': self.counter}
        return s
    
    def __repr__(self):
        return str(self.getJSON())

    def set(self, job):
        self.jobId = job['jobId']
        self.iteration = job['iteration']
        self.vmIp = job['vmIp']
        self.paraSigma = job['paraSigma']
        self.paraEA = job['paraEA']
        self.running = job['running']
        self.finished = job['finished']
        self.result = job['result']
        self.counter = job['counter']



class VM():
    def __init__(self, key_name=None, json=None):
        self.key_name = key_name
        if json == None:
            self.ip = '0.0.0.0'
            self.vmtype = ''
            self.dateUpdate = str(datetime.date.now())
        else:
            self.set(json)

    def getJSON(self):
        return { 'ip'         : self.ip,
                 'vmtype'     : self.vmtype,
                 'dateUpdate' : self.dateUpdate }

    def __repr__(self):
        return "ip: " + str(self.ip) + " vmtype: " + str(self.vmtype) + " dataUpdate: " + str(self.dateUpdate)

    def set(self, vm):
        self.ip = vm['ip']
        self.vmtype = vm['vmtype']
        self.dateUpdate = vm['dateUpdate']



def gae_get_job(url):
    # GET single job test
    conn =  httplib.HTTPConnection(url)
    conn.request('GET', '/get/job/')
    result = conn.getresponse()
    if result.status != 200:
        print "[E] got HTTP status %d" % result.status
        return None

    data = result.read()
    conn.close()
    return data

def gae_put_job(url, job):
    # HTTP PUT Job's
    conn =  httplib.HTTPConnection(url)
    body_content = json.dumps({ 'jobs' : [ job.getJSON() ] }, indent=2)
    headers = { "User-Agent": "python-httplib" }
    conn.request('PUT', '/put/job/', body_content, headers)
    result = conn.getresponse()
    conn.close()
    if result.status != 200:
        print "[E] got HTTP status %d" % result.status
    return result.status

def gae_get_vm(url):
    conn =  httplib.HTTPConnection(url)
    conn.request('GET', '/get/vm/')
    result = conn.getresponse()
    if result.status != 200:
        print "[E] got HTTP status %d" % result.status
        return None

    data = result.read()
    conn.close()
    return data

def get_vm(url):
    data = gae_get_vm(url)
    if data == None:
        return None
    jdata = json.loads(data)
    if jdata.has_key['vms']:
        for vm in jdata['vms']:
            return VM(keyname=str(vm['ip']), json=vm)

    return None

def gae_put_vm(url, vm):
    conn =  httplib.HTTPConnection(url)
    body_content = json.dumps({ 'vms' : [ vm.getJSON() ] }, indent=2)
    headers = { "User-Agent": "python-httplib" }
    conn.request('PUT', '/put/vm/', body_content, headers)
    result = conn.getresponse()
    conn.close()
    if result.status != 200:
        print "[E] got HTTP status %d" % result.status
    return result.status

def get_unique_job(url):
    data = gae_get_job(url)
    if data == None:
        return None
    jdata = json.loads(data)
    if jdata.has_key('jobs'):
        for job in jdata['jobs']:
            j = Job(key_name=str(job['jobId']), json=job)
            # Sanity test since I also get already finished jobs
            if j.result == None and j.finished != True and j.running == False:
                j.running = True
                if gae_put_job(url, j) != 200:
                    return None     # We couldn't claim the job, wait for the next turn
                return j

    return None

def get_parameters_in(job):
    return """group | name | value
algo | T                   | 100
algo | convCrit            | 1e-6
algo | newPolicyFlag       | 1
algo | storeStartingPoints | 0
algo | nSimulations        | 1e6
sspa | wGridSize           | 11
econ | gamma               | 2
econ | beta                | 0.99
econ | alphaA              | 0.5
econ | alphaB              | 0.5
econ | b1Abar              | -1
econ | b2Abar              | -1
econ | b1Bbar              | -1
econ | b2Bbar              | -1
econ | wBar                | -0.100
econ | wGridBar            | -0.100
hbit | EA                  | %f
hbit | EB                  | %f
hbit | sigmaA              | %f
hbit | sigmaB              | %f
hbit | gridScaleA          | 1
hbit | gridScaleB          | 1
hbit | gridSizeA           | 3
hbit | gridSizeB           | 3
algo | simulOnly           | 0
algo | policPlot           | 0
algo | simulPlot           | 0
algo | makeSav             | 0
algo | simulWealth0        | 0
""" % (job.paraEA, job.paraEA, job.paraSigma, job.paraSigma)

def create_workenv(job):
    w = str(job.jobId)
    if os.path.exists(w):
        print "[-] Workdir for job %d already exists, assuming a previous job was canceled" % job.jobId
        shutil.rmtree(w)

    os.mkdir(w)
    os.mkdir(os.path.join(w, 'output'))
    shutil.copytree(SKEL_INPUT, os.path.join(w, 'input'))
    shutil.copy(os.path.join(BIN_PATH, BIN), w)

    f = open(os.path.join(w, 'input', 'parameters.in'), 'w')
    f.write(get_parameters_in(job))
    f.close()

def call_forwardPremiumOut(job):
    w = str(job.jobId)
    print "[+] Running %s for job %d" % (BIN, job.jobId)
    job.proc = subprocess.Popen(os.path.join('.', BIN), cwd=w, shell=False,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def gather_results(job):
    ffb = PENALTY
    w = str(job.jobId)
    f = open(os.path.join(w, 'output', 'simulation.out'))
    for line in f:
        result = R_FAMA_FRENCH_BETA.match(line)
        if result:
            ffb = float(result.group(1))
            print "[+] Job %d got FamaFrenchBeta %f" % (job.jobId, ffb)
            break

    f.close()
    return ffb

def main():

    os.chdir(WORKDIR)

    print "[+] ForwardPremium dispatcher starting up..."
    """
    vm = None
    while not vm:
        vm = gae_get_vm(URL)
        time.sleep(10)

    print "[+] Got VM: %s" % vm
    """
    jobs = []

    while True:
        # Core with nothing to do -> get a new job
        if len(jobs) < NCORES:
            job = get_unique_job(URL)
            if job == None:
                print "[-] No new job found, waiting..."
            else:
                print "[+] Got eligible job with ID %d" % job.jobId
                create_workenv(job)
                call_forwardPremiumOut(job)
                jobs.append(job)

        print "[+] Checking job states (%d/%d running)" % (len(jobs), NCORES)
        for job in jobs:
            proc = job.proc
            # Check if the job terminated
            if proc is not None and proc.poll() is not None:
                job.running = False
                job.finished = True
                job.result = PENALTY  # gets updated by gather_results

                rc = proc.returncode
                if rc == 0:
                    job.result = gather_results(job)
                    if gae_put_job(URL, job) == 200:
                        print "[+] Successfully completed job %d (FFB=%f)" % (job.jobId, job.result)
                        shutil.rmtree(str(job.jobId))
                        jobs.remove(job)
                    else:
                        print "[E] Failed to submit completed job to GAE, trying again later"
                else:
                    print "[E] Job %d terminated with code %d" % (job.jobId, rc)
                    print "[E] stderr:"
                    print proc.stderr.read()
                    print "[E] stdout:"
                    print proc.stdout.read()
                    if gae_put_job(URL, job) == 200:
                        print "[+] Completed job %d with PENALTY (FFB=%f)" % (job.jobId, job.result)
                        shutil.rmtree(str(job.jobId))
                        jobs.remove(job)
                    else:
                        print "[E] Failed to submit completed job to GAE"

        #gae_put_vm(URL, vm)

        # wait between 5 and 10 seconds to prevent several VMs from accessing GAE simultaneously
        time.sleep(random.randrange(5, 10))

if __name__ == '__main__':
    main()
