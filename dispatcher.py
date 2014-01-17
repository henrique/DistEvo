#!/usr/bin/env python

import time, sys
import multiprocessing
import random
import numpy as np

from gae_lib import PENALTY_VALUE, putJob, getNextJob


NCORES = multiprocessing.cpu_count()


class Dispatcher():
    def __init__(self, eval_func, asynch=True):
        self.eval_func = eval_func
        self.asynch = asynch
        if asynch:
            self.pool = multiprocessing.Pool(processes=NCORES)  # start worker processes
        
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
        
        try:
            if not self.asynch:
                job.proc = self.eval_func(job.jobId, job.params)
            else:
                job.proc = self.pool.apply_async(self.eval_func, [job.jobId, job.params])
        except Exception as ex:
            print ex
            job.proc = None
        
    
    
    def gather_results(self, job):
        if not self.asynch:
            return job.proc
        else:
            try:
                return job.proc.get(timeout=1)
            except Exception as ex:
                print ex
                return PENALTY_VALUE
    
    
    
    def main(self):
    
#         os.chdir(WORKDIR)
    
        print "[+] dispatcher starting up..."
        jobs = []
    
        while True:
            jobs = self.run(jobs)
            time.sleep(0.1)
            
    
    
    
    def run(self, jobs):
            # Core with nothing to do -> get a new job
            while len(jobs) < (not self.asynch or NCORES): #run once on synchronous mode
                job = getNextJob()
                if job == None:
                    print "[-] No new job found, waiting..."
                    # wait between 5 and 15 seconds to prevent several VMs from accessing GAE simultaneously
                    time.sleep(random.randrange(5, 15))
                    break
                else:
                    print "[+] Got eligible job with ID %d" % job.jobId
                    job.time = time.time()
                    self.create_workenv(job)
                    self.call_evaluation(job)
                    jobs.append(job)
                    
            print "[+] %s Checking job states (%d/%d running)" % (time.strftime("%H:%M:%S"), len(jobs), NCORES)
            for job in jobs:
                if job.proc is None:
                    print "[E] No process information!"
                    print job
                    jobs.remove(job)
                    continue
                    
                # Check if the job terminated
                if not self.asynch or job.proc.ready(): #synchronous jobs were already done
                    job.running = False
                    job.finished = True
                    job.result = self.gather_results(job)
                    
                    if job.result is not None:
                        proc, job.proc = job.proc, None #temporally store proc
                        print job
                        if putJob(job):
                            print "[+] Successfully completed job %d (return=%f, time=%f)" % (job.jobId, job.result, time.time()-job.time)
                            jobs.remove(job)
                        else:
                            job.proc = proc
                            print "[E] Failed to submit completed job to GAE, trying again later"
                            time.sleep(random.randrange(1, 5))
                            
            return jobs


# test dispatcher
def test_evaluation(jobid, params):
    """The Rosenbrock function"""
    print "Rosenbrock (jobid=%d, params=%d) " % (jobid, len(params)), params
    time.sleep(.1)
    x = np.array(params)
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)


if __name__ == '__main__':
    Dispatcher(test_evaluation, not sys.flags.debug).main()
