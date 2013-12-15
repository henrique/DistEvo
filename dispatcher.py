#!/usr/bin/env python

import os, sys
import datetime, time
import httplib, json
import multiprocessing
import shutil
import subprocess
import re
import random

from config import *
from gae_lib import *
URL = server_target

NCORES = multiprocessing.cpu_count()

class Dispatcher():
    def __init__(self, eval_func):
        self.eval_func = eval_func
        
    def get_parameters_in(self, job):
        return job.params
    
    def create_workenv(self, job):
        return None
    #     w = str(job.jobId)
    #     if os.path.exists(w):
    #         print "[-] Workdir for job %d already exists, assuming a previous job was canceled" % job.jobId
    #         shutil.rmtree(w)
    # 
    #     os.mkdir(w)
    #     os.mkdir(os.path.join(w, 'output'))
    #     shutil.copytree(SKEL_INPUT, os.path.join(w, 'input'))
    #     shutil.copy(os.path.join(BIN_PATH, BIN), w)
    # 
    #     f = open(os.path.join(w, 'input', 'parameters.in'), 'w')
    #     f.write(get_parameters_in(job))
    #     f.close()
    
    
    def call_evaluation(self, job):
        print "[+] Running job %d" % (job.jobId)
        job.proc = self.eval_func(job)
    
    
    def gather_results(self, job):
        return job.proc
    
    
    
    def main(self):
    
#         os.chdir(WORKDIR)
    
        print "[+] dispatcher starting up..."
        """
        vm = None
        while not vm:
            vm = gae_get_vm(URL)
            time.sleep(10)
    
        print "[+] Got VM: %s" % vm
        """
        jobs = []
    
        while True:
            jobs = self.run(jobs)
            time.sleep(0.1)
            
    
    
    
    def run(self, jobs):
            # Core with nothing to do -> get a new job
            if len(jobs) < NCORES:
                job = getNextJob()
                if job == None:
                    print "[-] No new job found, waiting..."
                    # wait between 5 and 15 seconds to prevent several VMs from accessing GAE simultaneously
                    time.sleep(random.randrange(5, 15))
                else:
                    print "[+] Got eligible job with ID %d" % job.jobId
                    self.create_workenv(job)
                    self.call_evaluation(job)
                    jobs.append(job)
    
            print "[+] Checking job states (%d/%d running)" % (len(jobs), NCORES)
            for job in jobs:
                # Check if the job terminated
                if job.proc is not None:
                    job.running = False
                    job.finished = True
                    job.result = PENALTY_VALUE  # gets updated by gather_results
    
#                     if rc == 0:
                    job.result = self.gather_results(job)
                    if putJob(job):
                        print "[+] Successfully completed job %d (FFB=%f)" % (job.jobId, job.result)
#                         shutil.rmtree(str(job.jobId))
                        jobs.remove(job)
                    else:
                        print "[E] Failed to submit completed job to GAE, trying again later"
#                     else:
#                         print "[E] Job %d terminated with code %d" % (job.jobId, rc)
#                         print "[E] stderr:"
#                         print proc.stderr.read()
#                         print "[E] stdout:"
#                         print proc.stdout.read()
#                         if putJob(job):
#                             print "[+] Completed job %d with PENALTY (FFB=%f)" % (job.jobId, job.result)
#                             shutil.rmtree(str(job.jobId))
#                             jobs.remove(job)
#                         else:
#                             print "[E] Failed to submit completed job to GAE"
    
    #        gae_put_vm(URL, vm)
    
            return jobs


# test dispatcher
def test_evaluation(job):
    time.sleep(0.2)
    return sum(job.params) #will look for the smallest arg sum

if __name__ == '__main__':
    Dispatcher(test_evaluation).main()