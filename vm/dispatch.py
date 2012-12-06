#!/usr/bin/env python

import os
import time
import httplib
import json
import multiprocessing
import shutil
import subprocess
import re

# THIS IS SET BY THE DRIVER BEFORE PASSING IN USERDATA
MY_IP = '1.2.3.4'

# URL = 'localhost:8080'
URL = 'jcluster12.appspot.com'

SKEL_INPUT = '/opt/ifi/input'
BIN_PATH = '/apps/ifi'
BIN = 'forwardPremiumOut'
WORKDIR = '.'
NCORES = multiprocessing.cpu_count()

R_FAMA_FRENCH_BETA = re.compile(r"^FamaFrenchBeta:\s*(.*)$")

class Job():
    def __init__(self, key_name=None, json=None):
        self.key_name = key_name
        self.proc = None
        if json == None:
            self.jobId = 0
            self.vmIp = '0.0.0.0'
            self.paraSigma = None
            self.paraEA = None
            self.result = None
            self.running = False
            self.finished = False
        else:
            self.set(json)

    def getJSON(self):
        return { 'jobId'     : self.jobId,
                 'vmIp'      : self.vmIp,
                 'paraSigma' : self.paraSigma,
                 'paraEA'    : self.paraEA,
                 'running'   : self.running,
                 'finished'  : self.finished,
                 'result'    : self.result }

    def __repr__(self):
        return "jobId: " + str(self.jobId) + " vmIp: " + str(self.vmIp) + " paraSigma: " + str(self.paraSigma) + " paraEA: " + str(self.paraEA) + " running: " + str(self.running) + " finished: " + str(self.finished) + " result: " + str(self.result)

    def set(self, job):
        self.jobId = job['jobId']
        self.vmIp = job['vmIp']
        self.paraSigma = job['paraSigma']
        self.paraEA = job['paraEA']
        self.running = job['running']
        self.finished = job['finished']
        self.result = job['result']

def gae_get_job(url):
    # GET single job test
    conn =  httplib.HTTPConnection(url)
    conn.request('GET', '/get/jobs/')
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
    conn.request('PUT', '/put/', body_content, headers)
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
                print "[+] Got eligible job with ID %d" % j.jobId
                j.running = True
                j.vmIp = MY_IP
                if gae_put_job(url, j) != 200:
                    return None     # We couldn't claim the job, wait for the next turn
                return j

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
    w = str(job.jobId)
    f = open(os.path.join(w, 'output', 'simulation.out'))
    for line in f:
        result = R_FAMA_FRENCH_BETA.match(line)
        if result:
            ffb = float(result.group(1))
            print "[+] Job %d got FamaFrenchBeta %f" % (job.jobId, ffb)
            job.result = ffb
            break
    f.close()

def main():

    os.chdir(WORKDIR)
    jobs = []

    i = 0
    # while True:
    while i < 5:
        # Core with nothing to do -> get a new job
        if len(jobs) < NCORES:
            job = get_unique_job(URL)
            if job == None:
                print "[-] No new job found, time to sleep"
                continue

            create_workenv(job)
            call_forwardPremiumOut(job)
            jobs.append(job)

        print "[+] Checking job status (%d/%d running)" % (len(jobs), NCORES)
        for job in jobs:
            proc = job.proc
            # Check if the job terminated
            if proc is not None and proc.poll() is not None:
                job.running = False
                job.finished = True
                rc = proc.returncode
                if rc == 0:
                    gather_results(job)
                    if gae_put_job(URL, job) == 200:
                        print "[+] Successfully completed job %d (FFB=%f)" % (job.jobId, job.result)
                        shutil.rmtree(str(job.jobId))
                        jobs.remove(job)
                    else:
                        print "[E] Failed to submit completed job to GAE"
                else:
                    print "[E] Job %d terminated with code %d" % (job.jobId, rc)
                    print "[E] stderr:"
                    print proc.stderr.read()
                    print "[E] stdout:"
                    print proc.stdout.read()
                    job.result = 99.99
                    if gae_put_job(URL, job) == 200:
                        print "[+] Penalty for job %d (FFB=%f)" % (job.jobId, job.result)
                        shutil.rmtree(str(job.jobId))
                        jobs.remove(job)
                    else:
                        print "[E] Failed to submit completed job to GAE"

                i += 1

        # TODO: Update VM state on GAE
        time.sleep(10)

if __name__ == '__main__':
    main()
