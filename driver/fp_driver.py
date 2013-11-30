#! /usr/bin/env python

import time
import numpy as np
import datetime

from gc3libs.optimizer.dif_evolution import DifferentialEvolutionParallel
from fp_lib import *
from fp_ec2 import *

POPULATION_SIZE=100 #TODO 100
N_NODES=10

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

def calibrate_forwardPremium():
    """
    Drver script to calibrate forwardPremium EX and sigmaX parameters.
    It uses DifferentialEvolutionParallel as an implementation of
    Ken Price's differential evolution
    algorithm: [[http://www1.icsi.berkeley.edu/~storn/code.html]].
    """

    dim = 2 # the population will be composed of 2 parameters to  optimze: [ EX, sigmaX ]
    lower_bounds = [0.5,0.001] # Respectivaly for [ EX, sigmaX ]
    upper_bounds = [1,0.01]  # Respectivaly for [ EX, sigmaX ]
    y_conv_crit = 0.98 # convergence treshold; stop when the evaluated output function y_conv_crit

    # define constraints
    ev_constr = nlcOne4eachPair(lower_bounds, upper_bounds)

    opt = DifferentialEvolutionParallel(
        dim = dim,          # number of parameters of the objective function
        lower_bds = lower_bounds,
        upper_bds = upper_bounds,
        pop_size = POPULATION_SIZE,   # number of population members
        de_step_size = 0.85,# DE-stepsize ex [0, 2]
        prob_crossover = 1, # crossover probabililty constant ex [0, 1]
        itermax = 20,      # maximum number of iterations (generations)
        x_conv_crit = None, # stop when variation among x's is < this
        y_conv_crit = y_conv_crit, # stop when ofunc < y_conv_crit
        de_strategy = 'DE_local_to_best',
        nlc = ev_constr # pass constraints object
      )

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
        opt.new_pop = opt.draw_initial_sample()

        putJobs(pop2Jobs(opt))

    else: # finished?
        finished = True
        for job in pop:
            finished &= job.finished
#            if job.iteration > opt.cur_iter:  #restore current iteration counter
#                opt.cur_iter = job.iteration

        if finished:
            # Update population and evaluate convergence
            newVals = []
            opt.new_pop = np.zeros( (POPULATION_SIZE, dim) )
            k = 0
            for job in pop:
                newVals.append(job.result if job.result != None else PENALTY_VALUE)
                opt.new_pop[k,:] = (job.paraEA, job.paraSigma)
                k += 1

            # Update iteration count
#            global cur_iter, bestval
            opt.cur_iter += 1
#            opt.cur_iter = cur_iter
#            opt.bestvtest/fp_lib.pyal = bestval #!!!
#            opt.vals = newVals #!!!
#            opt.pop = opt.new_pop #!!!

            opt.update_population(opt.new_pop, newVals)
#            bestval = opt.bestval #!!!

            if not opt.has_converged():
                # Generate new population and enforce constrains
                opt.new_pop = opt.enforce_constr_re_evolve(opt.modify(opt.pop))

                # Push and run again!
                putJobs(pop2Jobs(opt))

            else:
                # Once iteration has terminated, extract `bestval` which should represent
                # the element in *all* populations that lead to the closest match to the
                # empirical value
                EX_best, sigmaX_best = opt.best

                print "Calibration converged after [%d] steps. EX_best: %f, sigmaX_best: %f" % (opt.cur_iter, EX_best, sigmaX_best)
                # TODO: Cleanup
                sys.exit()


    # VM's: create and manage dispatchers
    vms = getVMs()

    if not vms: # empty
        print "[+] No running EC2 instances found, creating %d" % N_NODES
        nodes = fp_ec2_create_vms(N_NODES, pubkey_file='/home/tklauser/.ssh/id_rsa.pub')
        vms = []
        for node in nodes:
            vm = { 'ip' : node.public_ips[0], 'vmtype' : 'Amazon', 'dateUpdate' : str(datetime.datetime.now()) }
            vms.append(vm)
        putVMs(vms)
    else:
        pass  #TODO manage VMs

    # Then, we could also run the forwardPremium binary here; Single script solution

    LocalState.save("driver", opt)

if __name__ == '__main__':
    while 1:
        calibrate_forwardPremium()
        time.sleep(5)
