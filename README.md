DistEvo
=======

Python Distributed Evolution with Google App Engine


Evolutionary algorithms
---------------------

The evolutionary optimization process is inspired by biology and natural selection. It can be said that all existent populations of organisms slowly converged to an optimal state due to selection of the fittest individuals through many different natural processes. Mutations and/or sexual breeding lead to variation between generations and within the generation itself, however, only successful individuals are allowed to breed or replicate further.
This darwinian process can be used as inspiration and applied to a black box optimization algorithm. For any given function, its set of parameters can be used as a genotype for its fitness, which is nothing but the proximity from this function result to a minimum, maximum or any other desired value. In other words, we can select the best parameters of a given sample population by simply comparing their values. Virtually any function can be used in this kind of optimization and no additional assumptions are necessary like linearity, existence of a derivative of any order, continuity, lack of noise, etc.
The most implementations of these group of algorithms, as well as ours, follow the simple steps below:
generate an initial population by random sampling;
calculate the fitness of this population;
create a new population by mutation and/or crossover;
calculate the fitness of this new population and replace their parents if the results are better
repeat the last two steps until convergence. 


Evolution strategy
---------------------

There are many variants for this simple algorithm specially on how the new populations are generated. Many different strategies can be used in this step to avoid local minima and accelerate the convergence. The current implementation uses the known and popular Differential evolution, which offer various strategy variants. Please find more about it and how to set its parameters on the following sections.



Components
---------------------

The implementation in this library divides the evolutionary optimization in three distinct components:
A driver, which controls the sampling population and its evolution according to a given strategy; 
A dispatcher, that executes the jobs created by the driver evaluating each individual of the population;
And a central server, which will keep the current jobs to be distributed between the different dispatchers.

The central server also has an additional function of archiving every iteration and can be used to generate a statistical analysis of the run. 


    
### Driver
    
The driver is responsible for the sample population used in the optimization. It will create the first population randomly within defined bounds and submit this population to the server to be evaluated. The script has to constantly poll the server to check for the conclusion of the evaluation and then run the evolution strategy in order to create a new candidate population. Then each individual is compared to its parent and the best will remain in the next round. Repeatedly, a new candidate population is created and evaluated until convergence.
Population size, parameters bounds, evolution and convergence strategies can be set by the user during the optimization setup. These parameters strongly depend on the proposed task and can drastically influence the results. Most of them should be quite straightforward to set but some will require some testing. As mentioned above, in this library we use an implementation of the differential evolution strategy, which offers its own set of parameters. Some information related to Differential Evolution can be found in the following papers:
Tvrdik 2008: http://www.proceedings2008.imcsit.org/pliks/95.pdf
Fleetwood: http://www.maths.uq.edu.au/MASCOS/Multi-Agent04/Fleetwood.pdf
Piyasatian: http://www-personal.une.edu.au/~jvanderw/DE_1.pdf
evolve_fn() is an adaptation of the following MATLAB code: http://www.icsi.berkeley.edu/~storn/DeMat.zip hosted on http://www.icsi.berkeley.edu/~storn/code.html#deb1.




### Dispatcher

The dispatcher script is the most simple part of the implementation but is still probably one of the most important. Here is where the work gets done. The daemon-like endless loop polls the server for new jobs and evaluate the population individuals created by the driver. A job normally constitutes of a simple set of parameters to be evaluated and some control and synchronization data. As in other optimization toolboxes, the result written back by the dispatcher is a single dimensional cost, which can be easily compared and ranked.


### Central server

The distributed environment still needs a central place to exchange data and synchronize the optimization progress. In our implementation this central point is a very simple database with a REST-like interface [Fielding et al. 2002]. The current version of DistEvo only supports the Google App Engine infrastructure, as we will see in the following sections, but its simplicity allows further extension and deployment in virtually any kind of web server. There is no assumptions of 100% server uptime, as the slave-processes will simply wait, but data loss should be avoided.



### System architecture
    
The distributed architecture works in a very simple Master/Slave model, where multiple slave machines will do the job drawn by a central controller. In our case the driver script would be also be part of the master component but it was separated from the server for simplicity, as most third-party service providers will have some kind of software restriction.

In the current implementation still runs the driver on a slave machine. This was due to initial incompatibility between the server infrastructure and the dependencies of our evolutionary strategies. However, this could be easily changed to facilitate integration and maintenance.  Nevertheless, the driver is reliable to crashes and restarts so it is usable and reliable as it is already.



Dependencies
---------------------

DistEvo heavily depends on python-numpy on both distributed scripts and the central google app engine server. Python-matplotlib is also used by the stattistical page on the server and the driver script has currently also a thin dependency to the gc3pie library, which can be acquired from: http://gc3pie.readthedocs.org/en/latest/users/install.html. However, only it is implementation of differential evolution is used and this involves only a couple of classes, which could be easily decoupled to facilitate deployment.


Installing
---------------------

All the dependencies can be easily met by installing their latest stable version. Apart from gc3pie, which was already mentioned above, you will only need to install python-numpy python-matplotlib. For example on Ubuntu:

    sudo apt-get install -y python-numpy python-matplotlib

You can also choose to use your preferable package system for python like pip or easy_install. After checking your PYTHONPATH we are ready to go.


### Google App Engine

For the moment we only support running the central server on Google App Engine (GAE), however the implementation only requires a very simple REST API which could be met by any kind of web server. The cloud infrastructure of GAE has the advantage of been very reliable and scalable, and it has a free version for testing with quite reasonable daily quotas.
You can simply install their SDK from: https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python and run:

    ./dev_appserver.py path/to/DistEvo/webapp

This command will start the GAE development server and its local database.


Testing & running
---------------------
    
Each file within distEvo should be testable by itself, by simply running it as a script. The main start point is optimizer.py, which when run will start the whole chain of optimization using a multi-dimensional Rosenbrock function for testing. This script can be used to run a multi-core dispatcher and optionally also an optimization driver by simply running:

    ./optimizer.py -jd

You could run the driver and the dispatcher in separate processes but the helper script optmizer.py can effitiently run both in parallel, as the driver does not use much CPU power and can safelly wait for the conclusion of the availabel jobs.


Creating your own optimization
---------------------

The optimizer.py is also the best sample for an optimization script. In other to run your own cost or fitness function you will need to implement a small script similar to the code below:

    #! /usr/bin/env python
    import numpy as np
    from optimizer import BaseOptimization, OptimizationCmd
    
    # test dispatcher
    def test_evaluation(jobid, params):
        """The Rosenbrock function"""
        print "Rosenbrock (jobid=%d, params=%d) " % (jobid, len(params)), params
        x = np.array(params)
        return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)
    
    def main():
        """ Test 3D Optimization """
        lower_bounds = np.array([0.0, 0.0, 0.0])
        upper_bounds = np.array([2.0, 2.0, 2.0])
        opt = BaseOptimization(population_size=20, lower_bounds, upper_bounds, test_evaluation)
        OptimizationCmd(opt).run()
    
    if __name__ == '__main__':
        main()

The evaluation function can be virtually any cost function you wish to minimize. If you have instead a fitness function to maximize, the negative fitness should be returned converting your maximization problem into a minimization one.


Optimization parameters
---------------------

The optimization driver can handle a series of parameters, which can strongly influence the result and the speed of convergence. It is up to you to choose and experiment with the parameters but some rule-of-thumb tips can be found here and in other references already mentioned in section Driver above. Please see below a complete list of available parameters for the current implementation:

Population size: define the size of the samples population used for the optimization. This value regulates the exploration and sampling density of the search space and is crucial for a good approximation to the global minimum, especially on higher dimensional parameter spaces.

Strategy: Allowed values are:
DE_rand: The classical version of Differential Evolution (DE), which uses crossover between current, best and another random individual.
DE_local_to_best: A version which has been used by quite a number of scientists. Attempts a balance between robustness and fast convergence.
DE_best_with_jitter: Tailored for small population sizes and fast convergence. Dimensionality should not be too high.
DE_rand_with_per_vector_dither: Classical DE with dither to become even more robust.
DE_rand_with_per_generation_dither: Classical DE with dither to become even more robust. Choosing de_step_size = 0.3 is a good start here.
DE_rand_either_or_algorithm: Alternates between differential mutation and three-point- recombination.

de_step_size: Differential Evolution step size.

prob_crossover: Probability new population draws will replace old members.

exp_cross: Set True to use exponential crossover.

itermax: Maximum number of iterations.

dx_conv_crit: Abort optimization if all population members are within a certain distance to each other.

y_conv_crit: Declare convergence when the target function is below a y_conv_crit.

upper_bounds and lower_bounds: Define population bounds for initialization as well as on every evolution step.



Script usage
---------------------

The optimizer.py scripts is provided with a parameter parser and can directly set some options for optimization process itself. You can get the current usage and available parameter by running the script with the -h or --help as showed on the table below:

    ./optimizer.py -h
    Usage: python optimizer.py [-djs:h] [--driver] [--jobs] [--server=] [--help]
    -d        --driver          Starts optimization driver to manage population.
    -j        --jobs            Use asynchronous multiprocess jobs.
    -s[url]    --server=[url]   DistEvo server URL. Takes hostname:port as arguments.
                                E.g. --server=localhost:8080
    -h        --help            Show this usage description.

--driver or -d will start the optimization driver in parallel to the dispatcher, which is a quite practical thing to do as the driver does not use much CPU time and it also helps reducing the amount of network communication by sharing the status information between the two components.
--jobs or -j uses python’s multiprocess API to create a pool of dispatchers. The size of this pool is determined by the numbers of cores available in the machine. Therefore, an evaluation is individually started on every single core avoiding parallelization problems.
--server=URL or -sURL is used to setup the target server URL. The default is the local server on port 8080, which is the default configuration from the development environment of Google App Engine.
