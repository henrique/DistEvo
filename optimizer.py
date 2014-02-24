#! /usr/bin/env python

import time, random, sys
from gae_config import gae_config

from driver import drive_optimization
from dispatcher import Dispatcher, test_evaluation


class BaseOptimization:
    """ Starts optimization driver and dispatcher """
    
    def __init__(self, population_size, lower_bounds, upper_bounds, eval_func):
        self.eval_func = eval_func
        self.population_size = population_size
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        self.dim = len(upper_bounds)
    
    def run(self, driver=True, asynch=True):
        disp = Dispatcher(self.eval_func, asynch)
        
        while True:
            if disp.run(): #jobs done
                if driver:
                    if drive_optimization(population_size=self.population_size, dim=self.dim, lower_bounds=self.lower_bounds, upper_bounds=self.upper_bounds):
                        continue
            
            # wait between 5 and 15 seconds to prevent several VMs from accessing GAE simultaneously
            time.sleep(random.randrange(5, 15))
            



class OptimizationCmd:
    """ Parses script arguments and starts optimization """
    
    #          [[args?, short, long, description]]
    descOpts  = [ \
                 [0, "d", "driver", "Starts optimization driver to manage population."],
                 [0, "j", "jobs", "Use asynchronous multiprocess jobs. (Not compatible with most debuggers)"],
                 [1, "s", "server", "DistEvo server URL. Takes hostname:port as arguments. E.g. --server=localhost:8080"],
                 [0, "h", "help", "Show this usage description."],
                ]

    #shortopts, longopts = "hds:", ["help", "driver", "server="]
    longopts =  [(l+'=' if a else l) for a,s,l,d in descOpts]
    shortopts = ''.join([(s+':' if a else s) for a,s,l,d in descOpts])
    
    
    def __init__(self, opt):
        self.opt = opt
        
        
    def usage(self):
        print 'Usage: python %s [-%s]' % (str(sys.argv[0]).rpartition("/")[-1], self.shortopts), \
              ' '.join(['[--%s]' % opt for opt in self.longopts])
        print '\n'.join(['-{0:8} --{1:14} {2}'.format((s+'[arg]' if a else s), (l+'=[arg]' if a else l), d) \
               for a,s,l,d in self.descOpts])
        
        
    def run(self):
        _driver, _asynch = False, False
        
        import getopt
        try:                                
            opts, args = getopt.getopt(sys.argv[1:], self.shortopts, self.longopts)
            #print opts, args
        except getopt.GetoptError as er:
            print er
            self.usage()
            sys.exit(2)
            
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()                     
                sys.exit()
            elif opt in ("-d", "--driver"):
                print "Starting optimization driver"
                _driver = True
            elif opt in ("-j", "--jobs"):
                print "Using multiprocess jobs mode"
                _asynch = True
            elif opt in ("-s", "--server"):
                gae_config.setServerURL(arg)
                
        self.opt.run(driver=_driver, asynch=_asynch)
    


def main():
    """ Test 3D Optimization """
    import numpy as np
    lower_bounds = np.array([0.0, 0.0, 0.0])
    upper_bounds = np.array([2.0, 2.0, 2.0])
    opt = BaseOptimization(20, lower_bounds, upper_bounds, test_evaluation)
    OptimizationCmd(opt).run()

if __name__ == '__main__':
    main()
