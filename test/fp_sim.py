#! /usr/bin/env python
import time
import random

from fp_lib import *


if __name__ == '__main__':
    #testing: simulates the VM's
    while 1:
        job = getNextJob()
        if job:
            if not job.running:
                job.running = True
                putJob(job)
                time.sleep(1)
#            else:
            job.finished = True
            job.result = float(random.randrange(100, 100000))/100
            putJob(job)
        
        getJobs()
        time.sleep(2)
