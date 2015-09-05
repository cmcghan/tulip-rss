# Copyright (c) 2015 by California Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the California Institute of Technology nor
# the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior
# written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CALTECH
# OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Changelog:
-- initial commit of cleaned-up copy, 2015-09-04 CLRM

=== Summary of contents ===

Examples used in Space 2015 paper: C. McGhan and R.Murray, "Application of
Correct-by-Construction Principles for a Resilient Risk-Aware Architecture".

"""

# originally modified from: controlled_switching.py (and others)

# WARNING: This example may not yet be working.  Please check again in
#          the upcoming release.
#
# This is an example to demonstrate how a Tower of Hanoi game might be
# constructed, which tulip could solve to create a finite state machine / 
# action strategy / policy to win the game.
#
# We start with a no-environment-as-aggressor game.

from tulip import spec, synth, transys
import numpy as np
from scipy import sparse as sp

#
# Deliberative Layer action-planning/scheduling example:
#
# init: s1 (or s3) of the following transition system
#
#          a12_1      a23_1
#      s1 ------> s2 ------> s3 -
#      | -------->  -------->   |
#      | |  a12_2      a23_2    |
#      |  |                     | a35_1
# a14_1 |  |----                |
#       |   |   ---             |
#      \|/   |     ---a15_1     |
#       s4    ----    ---       |
#         |  a15_2----   ---   \|/
#         ---------   ----->--> s5
#            a45_1 |---------->
#
# goal: s5, with pic at s2 and s5, and with sample from s5, (and with fuel>0 and risk<20)
#


"""

stuff below is "version X" with pretty-printing, no env. states, and fuel/energy with 'wait' action, but no risk

"""

def energyStr(lo=0,hi=10,drop=0):
    # get energy statement set up correctly
    energystr = '( '
    for i in range(lo+drop,hi+1):
#        energystr += '(energy=%d -> X(energy=%d)) && ' % (i,i-drop) # energy level stays the same
        energystr += '(X(energy=%d) <-> (energy=%d)) && ' % (i-drop,i) # energy level stays the same
    energystr = energystr[0:len(energystr)-4] # remove trailing ' && '
    energystr += ' )'
    return energystr

def dropStr(namestr,lo=0,hi=10,drop=0):
    """ get energy and/or risk statement set up correctly
    inputs:
    namestr is a string = 'energy', or 'risk', or etc.
    lo is an integer (default=0)
    hi is an integer (default=10)
    drop is an integer (default 0)
    outputs:
    string in the form ( (X(energy=0) <-> (energy=5)) && (X(energy=1) <-> (energy=6)) && (X(energy=2) <-> (energy=7)) ) for lo=0,hi=7,drop=5
    """
    dropstr = '( '
    for i in range(lo+drop,hi+1):
        dropstr += '(X(%s=%d) <-> (%s=%d)) && ' % (namestr,i-drop,namestr,i) # energy/risk level stays the same, drops if drop>0
    dropstr = dropstr[0:len(dropstr)-4] # remove trailing ' && '
    dropstr += ' )'
    return dropstr

def riseStr(namestr,lo=0,hi=10,rise=0):
    """ get energy and/or risk statement set up correctly
    inputs:
    namestr is a string = 'energy', or 'risk', or 'stepCounter', or etc.
    lo is an integer (default=0)
    hi is an integer (default=10)
    rise is an integer (default 0)
    outputs:
    string in the form ( (X(energy=1) <-> (energy=0)) && (X(energy=2) <-> (energy=1)) && (X(energy=3) <-> (energy=2)) ) for lo=0,hi=3,rise=1
    """
    risestr = '( '
    for i in range(lo,hi+1-rise):
        risestr += '(X(%s=%d) <-> (%s=%d)) && ' % (namestr,i+rise,namestr,i) # energy/risk level stays the same if 0, rises if rise>0
    risestr = risestr[0:len(risestr)-4] # remove trailing ' && '
    risestr += ' )'
    return risestr

def runPaperExample(exampleRun,ver='1',riskgt=17,energygt=0):

    # set initial variables
    if (exampleRun == 'test1'):
        ver = '1'
        riskgt = 17
        energygt = 0
    elif (exampleRun == 'test2'):
        ver = '2'
        riskgt = 17
        energygt = 6
    elif (exampleRun == 'test3'):
        ver = '3'
        riskgt = 16
        energygt = 6

    # set logfile
    import logging
    logging.basicConfig(filename='deliberative_action_planner_%s.log' % ver,
                        level=logging.INFO, filemode='w') # level=logging.DEBUG
    logger = logging.getLogger(__name__)
    
    # Create a finite transition system
    sys_sws = transys.FTS() # system actions only, no (open) env. yet
    
    # add the states and actions
    #sys_sws.states.add_from(['s1','s2','s3','s4','s5'])
    for i in range(1,5+1):
        sys_sws.states.add('s' + str(i))
    
    #sys_sws.actions.add_from(['a12_1','a12_2','a23_1', 'a23_2', 'a15_1', 'a15_2', 'a14_1', 'a45_1', 'a35_1'])
    # then set up the transitions (state1, action1 -> state2)
    for numlist in [[1,2,2],[2,3,2],[1,5,2],[1,4,1],[4,5,1],[3,5,1]]:
        st1 = numlist[0] # [s"#1" loc1, s"#2" loc2, number of actions a"#1#2_#"]
        st2 = numlist[1]
        numactions = numlist[2]
        st1str = 's' + str(st1)
        st2str = 's' + str(st2)
        #sys_sws.states.add_from([st1str,st2str]) # could do this instead of above
        for i in range(1,numactions+1):
            astr = 'a' + str(st1) + str(st2) + '_' + str(i)
            sys_sws.actions.add(astr) # could do this instead of above
            sys_sws.transitions.add(st1str,st2str,actions=astr)
            sys_sws.transitions.add(st2str,st1str,actions=astr)
    
    # then set up transitions for (state1, wait -> state1)
    sys_sws.actions.add('wait')
    for st1 in range(1,5+1):
        st1str = 's' + str(st1)
        sys_sws.transitions.add(st1str,st1str,actions='wait')
    
    # set s1 as initial state
    initial_state_str = 's1'
    #initial_state_str = 's2'
    sys_sws.states.initial.add(initial_state_str)
    
    # This is what is visible to the outside world (and will go into synthesis method)
    print(sys_sws) # show the Finite Transition System, make sure it was encoded properly
    sys_sws.save('deliberative_%sa.pdf' % ver) # save the visual diagram of the FTS, for same reason
    # sys_sws.save() shows all possible transitions between states according to actions
    
    print("Done saving deliberative_%sa.pdf" % ver)
    
    #
    # Environment variables and specification
    #
    # The environment can issue a park signal that the robot just respond
    # to by moving to the lower left corner of the grid.  We assume that
    # the park signal is turned off infinitely often.
    #
    env_vars = set() # empty set
    env_init = set() # empty set
    env_prog = set() # empty set
    env_safe = set() # empty set
    
    # 
    # System specification
    #
    # The system specification is that the robot should (repeatedly?) revisit
    # the rightmost spire (this is because there are no 'wait' or 'stay in same
    # state' actions currently).
     
    # does sys_vars actually use the "0" value? it doesn't seem to...
    # basically, looks like a "0" value pulls the value completely off the stack (as False?), in the 'atomic proposition' sense of things
    # so, we want to avoid using value=0 for this kind of stuff! ^_^
    # note: for gr1c, lower bound must be zero (0)
    
    print("Writing up goals and such for system")
    
    print("Writing up sys vars and such for system")
    
    sys_vars = dict()
    sys_init = set()
    sys_prog = set()
    sys_safe = set()
    
    sys_init |= {'sys_actions=wait'} # start in wait mode
    
    goalstr = 's5'
    #goalstr = 's3'
    sys_prog |= {'loc=%s' % goalstr} # goal --> []<> (get to s5)
    sys_safe |= {'loc=%s -> next(loc=%s)' % (goalstr,goalstr)} # then stay there forever # this didn't seem to work with the FTS before, now does for some reason, not sure what's going on...
    
    energylo=0
    energyhi=20
    sys_vars.update({'energy':(energylo,energyhi)})
    sys_init |= {'energy=%d' % energyhi}
    sys_safe |= {'energy > %d' % energygt} # must keep fuel/energy usage above energygt
    
    risklo = 0
    riskhi = 20
    sys_vars.update({'risk':(risklo,riskhi)})
    sys_init |= {'risk=%d' % riskhi}
    sys_safe |= {'risk > %d' % riskgt} # must keep risk usage above riskgt
    
    #                 0        1        2        3        4        5        6        7        8       9
    allactStr = ['a35_1', 'a23_1', 'a23_2', 'a12_1', 'a12_2', 'a15_2', 'a15_1', 'a45_1', 'a14_1', 'wait']
    alldropenergy = [ 4,       3,       6,       2,       3,       7,       6,       5,       3,      0]
    alldroprisk   = [ 1,       4,       0,       2,       1,       1,       2,       0,       0,      0]
    for actStr,energydrop,riskdrop in zip(allactStr,alldropenergy,alldroprisk):
        #energystr = energyStr(energylo,energyhi,energydrop)
        energystr = dropStr('energy',energylo,energyhi,energydrop)
        sys_safe |= {'sys_actions=%s -> (%s && (X(energy=0) <-> energy<=%d))' % (actStr,energystr,alldropenergy[i-1])} # wait action keeps energy at same level (no energy used)
        riskstr = dropStr('risk',risklo,riskhi,riskdrop)
        sys_safe |= {'sys_actions=%s -> (%s && (X(risk=0) <-> risk<=%d))' % (actStr,riskstr,alldroprisk[i-1])} # wait action keeps energy at same level (no energy used)
    
    #                 0  1  2  3  4
    #                 atakepicture#
    alldropenergy2 = [0, 0, 0, 0, 0]
    alldroprisk2   = [0, 0, 0, 0, 0]
    for i in range(1,5+1): # [1] atakepicture1,picAtS1Taken, ...
        actStr = 'atakepicture%d' % i
        energystr = dropStr('energy',energylo,energyhi,alldropenergy2[i-1])
        sys_safe |= {'sys_actions=%s -> (%s && (X(energy=0) <-> energy<=%d))' % (actStr,energystr,alldropenergy2[i-1])} # wait action keeps energy at same level (no energy used)
        riskstr = dropStr('risk',risklo,riskhi,alldroprisk2[i-1])
        sys_safe |= {'sys_actions=%s -> (%s && (X(risk=0) <-> risk<=%d))' % (actStr,riskstr,alldroprisk2[i-1])} # wait action keeps energy at same level (no energy used)
    
        actboolStr = 'picAtS%dTaken' % i
        locStr = 's%d' % i
        sys_sws.actions.add(actStr)
        sys_sws.transitions.add('s%d' % i,'s%d' % i,actions=actStr)
        sys_vars.update({actboolStr:'boolean'})
        sys_init |= {'!%s' % actboolStr}
        sys_safe |= {'(energy>%d && loc=%s && sys_actions=%s) -> X(%s)' % (alldropenergy2[i-1],locStr,actStr,actboolStr)}
        sys_safe |= {'(energy<=%d && loc=%s && sys_actions=%s) -> X(energy=0)' % (alldropenergy2[i-1],locStr,actStr)}
        sys_safe |= {'(sys_actions!=%s && !%s) -> (X(!%s))' % (actStr,actboolStr,actboolStr)} # don't allow other actions to arbitrarily set this to True
        sys_safe |= {'%s -> X(%s)' % (actboolStr,actboolStr)} # if picture is taken, 'stays' taken
    
    sys_prog |= {'picAtS2Taken'} # goal --> trying to take picture at s2
    
    #                 0  1  2  3  4
    #                 atakesample#
    alldropenergy3 = [1, 1, 1, 1, 1]
    alldroprisk3   = [0, 0, 0, 0, 0]
    for i in range(1,5+1): # [1] atakepicture1,picAtS1Taken, ...
        actStr = 'atakesample%d' % i
        energystr = dropStr('energy',energylo,energyhi,alldropenergy3[i-1])
        sys_safe |= {'sys_actions=%s -> (%s && (X(energy=0) <-> energy<=%d))' % (actStr,energystr,alldropenergy3[i-1])} # wait action keeps energy at same level (no energy used)
        riskstr = dropStr('risk',risklo,riskhi,alldroprisk3[i-1])
        sys_safe |= {'sys_actions=%s -> (%s && (X(risk=0) <-> risk<=%d))' % (actStr,riskstr,alldroprisk3[i-1])} # wait action keeps energy at same level (no energy used)
    
        actboolStr = 'samAtS%dTaken' % i
        locStr = 's%d' % i
        sys_sws.actions.add(actStr)
        sys_sws.transitions.add('s%d' % i,'s%d' % i,actions=actStr)
        sys_vars.update({actboolStr:'boolean'})
        sys_init |= {'!%s' % actboolStr}
        sys_safe |= {'(energy>%d && loc=%s && sys_actions=%s) -> X(%s)' % (alldropenergy3[i-1],locStr,actStr,actboolStr)}
        sys_safe |= {'(energy<=%d && loc=%s && sys_actions=%s) -> X(energy=0)' % (alldropenergy3[i-1],locStr,actStr)}
        sys_safe |= {'(sys_actions!=%s && !%s) -> (X(!%s))' % (actStr,actboolStr,actboolStr)} # don't allow other actions to arbitrarily set this to True
        sys_safe |= {'%s -> X(%s)' % (actboolStr,actboolStr)} # if sample is taken, 'stays' taken
    
    #sys_prog |= {'samAtS5Taken'} # goal --> trying to take sample at s5
    
    #
    # after all sys_goal specs are written...
    #
    
    goal_conditions = ''
    for goalpieceStr in list(sys_prog):
        goal_conditions += goalpieceStr + ' && '
    goal_conditions = goal_conditions[0:len(goal_conditions)-4] # remove trailing ' && '
    
    # set up stepcounter at the end of everything, after all sys_goal specs are written:
    steplo=0
    stephi=8 # lower this number to try and force gr1c to be more efficient
    sys_vars.update({'stepCounter':(steplo,stephi)})
    sys_init |= {'stepCounter=%d' % steplo}
    stepstr = riseStr('stepCounter',steplo,stephi,1)
    sys_safe |= {'!(%s) -> %s' % (goal_conditions,stepstr)} # goal_conditions not met implies stepCounter increases by 1 each time
    stepstr = riseStr('stepCounter',steplo,stephi,0)
    sys_safe |= {'(%s) -> %s' % (goal_conditions,stepstr)} # goal_conditions met implies stepCounter doesn't increase (any more)
    # then lower stephi to try and force gr1c to find a more efficient (shortest number of actions) solution
    sys_safe |= {'stepCounter < %d' % (stephi)} # must keep counter below stephi; requires below that we stop counting steps after we finish all goals
    
    # add this in so we can tell when we're just doing extra stuff post-whatever
    sys_vars.update({'sysgoalsReached':'boolean'})
    sys_init |= {'!sysgoalsReached'}
    sys_safe |= {'!(%s) <-> !sysgoalsReached' % (goal_conditions)} # goal_conditions not met implies sysgoals(not_yet)Reached
    sys_safe |= {'(%s) <-> sysgoalsReached' % (goal_conditions)} # goal_conditions met implies sysgoalsReached
    
    # changes might've been made this far down, so show again...
    print(sys_sws) # show the Finite Transition System, make sure it was encoded properly
    sys_sws.save('deliberative_%sb.pdf' % ver) # save the visual diagram of the FTS, for same reason
    
    print("Done saving deliberative_%sb.pdf" % ver)
    
    print("Creating spec for sys_sws system")
    
    # Create the specification
    specs = spec.GRSpec(env_vars=env_vars, sys_vars=sys_vars,
                        env_init=env_init, sys_init=sys_init,
                        env_safety=env_safe, sys_safety=sys_safe,
                        env_prog=env_prog, sys_prog=sys_prog)
    
    print(specs.pretty())
    
    # GRSpec(env_vars=None, sys_vars=None, env_init='', sys_init='', env_safety='', sys_safety='', env_prog='', sys_prog='')
    # (env_init & []env_safety & []<>env_prog_1 & []<>env_prog_2 & ...)
    #   -> (sys_init & []sys_safety & []<>sys_prog_1 & []<>sys_prog_2 & ...)
    # 
    # C{env_vars}: alias for C{input_variables} of L{LTL}, concerning variables that are determined by the environment
    # C{env_init}: a list of string that specifies the assumption about the initial state of the environment.
    # C{env_safety}: a list of string that specifies the assumption about the evolution of the environment state.
    # C{env_prog}: a list of string that specifies the justice assumption on the environment.
    # C{sys_vars}: alias for C{output_variables} of L{LTL}, concerning variables that are controlled by the system.
    # C{sys_init}: a list of string that specifies the requirement on the initial state of the system.
    # C{sys_safety}: a list of string that specifies the safety requirement.
    # C{sys_prog}: a list of string that specifies the progress requirement.
    
    print("Done creating spec for sys_sws system")
    
    # Controller synthesis
    #
    # At this point we can synthesize the controller using one of the available
    # methods.  Here we make use of gr1c.
    #
    print("Synthesizing solution for sys_sws system")
    ctrl = synth.synthesize('gr1c', specs, sys=sys_sws)
    print("Done synthesizing solution for sys_sws system")
    
    print("Creating .png file for sys_sws system")
    
    if ctrl is None:
        print("Got gr1c error, not attempting save =or= print-to-screen =or= MealyMachine dumpsmach")
    else:
        # Generate a graphical representation of the controller for viewing
        if not ctrl.save('deliberative_%s_sws.png' % ver):
            print("Couldn't save .png file, printing ctrl instead")
            print(ctrl)
            print("Done printing ctrl instead")
        print("Done creating .png file for sys_sws system")
        
        print("Writing MealyMachine out via dumpsmach")
        # ctrl is a MealyMachine
        from tulip import dumpsmach
        dumpsmach.write_python_case(filename='dumpsmachtest_dlap%s.py' % ver,M=ctrl,classname="TulipStrategy",start='Sinit')
        print("Done writing MealyMachine out to dumpsmachtest_dlap%s.py" % ver)

# --------------------------------------------------------------------------- #

if __name__ == '__main__':

    try:

        runPaperExample('test1')
        runPaperExample('test2')
        runPaperExample('test3')            


    except KeyboardInterrupt:
        pass;
