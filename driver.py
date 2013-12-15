#! /usr/bin/env python

import time
import numpy as np
import datetime

import gc3libs
from gc3libs import Application, configure_logger
from gc3libs.optimizer.dif_evolution import DifferentialEvolutionAlgorithm
from gc3libs.optimizer import draw_population
from gae_lib import *

POPULATION_SIZE=5 #TODO 100
# N_NODES=10


def drive_optimization(dim, lower_bounds, upper_bounds,
                 # DE-specific parameters
                 de_strategy = 'DE_local_to_best', de_step_size = 0.85, prob_crossover = 1.0, exp_cross = False,
                 # converge-related parameters
                 itermax = 100, dx_conv_crit = None, y_conv_crit = None,
                 # misc
                 in_domain=None, seed=None, logger=None, after_update_opt_state=[]):
    """
    Driver script
    It uses DifferentialEvolutionAlgorithm as an implementation of
    Ken Price's differential evolution
    algorithm: [[http://www1.icsi.berkeley.edu/~storn/code.html]].
    """

    if logger is None:
        configure_logger(level=logging.CRITICAL)
        logger = logging.getLogger("gc3.gc3libs")

    if in_domain is None:
        def _default_in_domain(pop):
            return (pop < upper_bounds).all(axis=1) & (pop > lower_bounds).all(axis=1)
        in_domain = _default_in_domain
 
    
    opt = DifferentialEvolutionAlgorithm(
        initial_pop = np.zeros( (POPULATION_SIZE, dim) ),
        de_step_size = de_step_size,# DE-stepsize ex [0, 2]
        prob_crossover = prob_crossover, # crossover probabililty constant ex [0, 1]
        itermax = itermax,      # maximum number of iterations (generations)
        dx_conv_crit = dx_conv_crit, # stop when variation among x's is < this
        y_conv_crit = y_conv_crit, # stop when ofunc < y_conv_crit
        de_strategy = de_strategy,
        logger = logger,
        in_domain = in_domain,
        )
    opt.vals = np.ones(POPULATION_SIZE)*sys.float_info.max #init

    try:
        tmp = LocalState.load("driver", opt)
        #print tmp, opt
    except:
        print 'Nothing to be loaded...'

    # Jobs: create and manage population
    pop = getJobs()

    if not pop: # empty
        # Initialise population using the arguments passed to the
        # DifferentialEvolutionParallel iniitalization
        opt.new_pop = draw_population(lower_bds=lower_bounds, upper_bds=upper_bounds, size=POPULATION_SIZE, dim=dim)

        putJobs(pop2Jobs(opt))

    else: # finished?
        finished = True
        for job in pop:
            finished &= job.finished
#            if job.iteration > opt.cur_iter:  #restore current iteration counter
#                opt.cur_iter = job.iteration

        if finished:
            # Update population and evaluate convergence
            newVals = np.zeros(POPULATION_SIZE)
            opt.new_pop = np.zeros( (POPULATION_SIZE, dim) )
            k = 0
            for job in pop:
                opt.new_pop[k,:] = job.params
                newVals[k] = (job.result if job.result != None else PENALTY_VALUE)
                k += 1

            # Update iteration count
#            global cur_iter, bestval
#             opt.cur_iter += 1
#            opt.cur_iter = cur_iter
#            opt.bestvtest/fp_lib.pyal = bestval #!!!
#            opt.vals = newVals #!!!
#            opt.pop = opt.new_pop #!!!

            opt.update_opt_state(opt.new_pop, newVals)
#            bestval = opt.bestval #!!!

            if not opt.has_converged():
                # Generate new population and enforce constrains
#                 opt.new_pop = opt.enforce_constr_re_evolve(opt.modify(opt.pop)) TODO!!!!
                opt.new_pop = opt.evolve()
                
                # Push and run again!
                putJobs(pop2Jobs(opt))
                print [opt.best_y, opt.best_x]
                
            else:
                # Once iteration has terminated, extract `bestval` which should represent
                # the element in *all* populations that lead to the closest match to the
                # empirical value

                print "Calibration converged after [%d] steps. " % (opt.cur_iter)
                print [opt.best_y, opt.best_x]
                # TODO: Cleanup
                sys.exit()


#     # VM's: create and manage dispatchers
#     vms = getVMs()
# 
#     if not vms: # empty
#         print "[+] No running EC2 instances found, creating %d" % N_NODES
#         nodes = fp_ec2_create_vms(N_NODES, pubkey_file='/home/tklauser/.ssh/id_rsa.pub')
#         vms = []
#         for node in nodes:
#             vm = { 'ip' : node.public_ips[0], 'vmtype' : 'Amazon', 'dateUpdate' : str(datetime.datetime.now()) }
#             vms.append(vm)
#         putVMs(vms)
#     else:
#         pass  #TODO manage VMs

    # Then, we could also run the forwardPremium binary here; Single script solution

    LocalState.save("driver", opt)
    


# test driver
if __name__ == '__main__':
    dim = 2 # the population will be composed of 2 parameters to  optimze: [ EX, sigmaX ]
    lower_bounds = np.array([0.5, 0.001]) # Respectivaly for [ EX, sigmaX ]
    upper_bounds = np.array([1, 0.01])  # Respectivaly for [ EX, sigmaX ]
    dx_conv_crit = 1e-5 # convergence treshold; stop when the evaluated output function y_conv_crit
    
    while 1:
        drive_optimization(dim=dim, lower_bounds=lower_bounds, upper_bounds=upper_bounds, dx_conv_crit=dx_conv_crit)
        time.sleep(5)
