# from: controlled_switching.py

# WARNING: This example may not yet be working.  Please check again in
#          the upcoming release.
#
# This is an example to demonstrate how the output of abstracting a switched
# system, where the dynamics are controlled through switching and
# if multiple transitions are possible from a state in some mode,
# then the system controls which one is taken.

# NO, 26 Jul 2013.

# We will assume, we have the 6 cell robot example.

#
#     +---+---+---+
#     | 3 | 4 | 5 |
#     +---+---+---+
#     | 0 | 1 | 2 |
#     +---+---+---+
#

from tulip import spec, synth, transys
import numpy as np
from scipy import sparse as sp


###############################
# Switched system with 4 modes:
###############################

# In this scenario we have limited actions "left, right, up, down" with 
# certain (nondeterministic) outcomes

# Create a finite transition system
sys_sws = transys.FTS()

sys_sws.actions.add_from({'right','up','left','down'})

# str states
n = 6
states = transys.prepend_with(range(n), 's')
sys_sws.states.add_from(set(states) )
sys_sws.states.initial.add_from({'s0', 's3'})

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws)
sys_sws.save('test20.pdf') # show all possible transitions between states according to actions

sys_sws.atomic_propositions.add_from(['home','lot'])
state_labels = [{'home'}, set(), set(), set(), set(), {'lot'}]

# Add states and decorate TS with state labels (aka atomic propositions)
for state, label in zip(states, state_labels):
    sys_sws.states.add(state, ap=label)

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws)
sys_sws.save('test21.pdf') # show all possible transitions between states according to actions



#
# Tower of Hanoi example:
#
# init:
#
#   -1-      |       |
#  --2--     |       |
# ---3---    |       |
# ========================
# goal:
#
#    |       |      -1-
#    |       |     --2--
#    |       |    ---3---
# ========================
#


# prepends are for pretty-printing things...
prepends = []
prepends.append('plate') # plate (smallest=1, middle=2, largest=3)
prepends.append('spire') # spire-rod (left=1, middle=2, right=3)
prepends.append('level') # level (highest=1, middle=2, lowest/base=3)
# assume that index 1 = plate num., index 2 = spindle-rod, index 3 = height
#initial_state = [[1,1],[1,2],[1,3]] # version 1
# or explicitly hold plate num. as first number, with position next:
#       [ [plate,[spire-rod,level]], ... ]
initial_state = [ [1,[1,1]], [2,[1,2]], [3,[1,3]] ] # version 2

def convertToLabel(state,prepends):
    labelstr = '{' # add '{' to beginning
    for plateInfo in state:
        labelstr += prepends[0] + str(plateInfo[0])
        i = 1
        for num in plateInfo[1]:
            labelstr += "-" + prepends[i] + str(num)
            i += 1
        labelstr += ' '
    labelstr = labelstr[0:len(labelstr)-1] # remove trailing ' '
    labelstr += '}' # add '}' to end
    return labelstr

def convertToAltLabel(state):
    # fill in matrix with zeros to start:
    holdgrid = [[0 for j in range(len(state))] for i in range(len(state))]
    # now, fill in positions with sizes of discs at actual locations
    for plateInfo in state:
        #print(plateInfo)
        loc = plateInfo[1]
        holdgrid[loc[1]-1][loc[0]-1] = plateInfo[0] # spire(0) = col, height(1) = row
    
    # simple labelstr:
    #labelstr = '{' # add '{' to beginning
    labelstr = ''
    i = int(0)
    for row in holdgrid:
        i += 1
        for j in row:
            labelstr += str(j) #+ ' '
        #labelstr = str(labelstr[0:len(str(labelstr))-1])
        # add one more '\' in front of the 'n' each time we '\n' <-- *** NOTE, THIS IS VERY BRITTLE 'PRETTY PRINTING'!
        if (i < len(holdgrid)): # don't put a '\\\...\n' on the last line
            if i == 1:
                labelstr += '\n'
            elif i%2 == 0: # i even
                labelstr += '\\'*(i/2) + 'n'
            else: # i odd
                labelstr += '\\'*(i/2) + '\n'
    #labelstr = labelstr[1:len(labelstr)-1] # remove leading ' ' and trailing '\n'
    #labelstr = labelstr[0:len(labelstr)-1] # remove trailing '\n'
#    labelstr += '}' # add '}' to end
    labelstr = '{' + str(labelstr) + '}' # add leading '{' and trailing '}'
    
#    labelstr2 = '{' + str(holdgrid[0][0]) + str(holdgrid[0][1]) + str(holdgrid[0][2]) + '\n' + str(holdgrid[1][0]) + str(holdgrid[1][1]) + str(holdgrid[1][2]) + '\\n' + str(holdgrid[2][0]) + str(holdgrid[2][1]) + str(holdgrid[2][2]) + '}'
#    labelstr3 = '{' + str(holdgrid[0][0]) + '-' + str(holdgrid[0][1]) + '-' + str(holdgrid[0][2]) + '_' + str(holdgrid[1][0]) + '-' + str(holdgrid[1][1]) + '-' + str(holdgrid[1][2]) + '_' + str(holdgrid[2][0]) + '-' + str(holdgrid[2][1]) + '-' + str(holdgrid[2][2]) + '}' # = convertToLabel()
#    labelstr4 = '{' + str(holdgrid[0][0]) + str(holdgrid[0][1]) + str(holdgrid[0][2]) + str(holdgrid[1][0]) + str(holdgrid[1][1]) + str(holdgrid[1][2]) + str(holdgrid[2][0]) + str(holdgrid[2][1]) + str(holdgrid[2][2]) + '}'
    labelstr5 = str(holdgrid[0][0]) + str(holdgrid[0][1]) + str(holdgrid[0][2]) + str(holdgrid[1][0]) + str(holdgrid[1][1]) + str(holdgrid[1][2]) + str(holdgrid[2][0]) + str(holdgrid[2][1]) + str(holdgrid[2][2])
    
    return labelstr5

def convertActionToStr(action): # [pl,[spa,lva],[spb,lvb]]
    return str(action[0])+str(action[1][0])+str(action[1][1])+str(action[2][0])+str(action[2][1])
    
holdstr = convertToAltLabel(initial_state)
print(holdstr)

#import sys
#sys.exitfunc(0)

print(convertToLabel(initial_state,prepends))

def convertToParseableStr(state):
    parseablestr = ''
    for plateInfo in state:
        parseablestr += str(plateInfo[0])
        i = 1
        for num in plateInfo[1]:
            parseablestr += '-' + str(num)
            i += 1
        parseablestr += '_'
    parseablestr = parseablestr[0:len(parseablestr)-1] # remove trailing ' '
    return parseablestr

def convertToParseableStr2(state): # same as convertToAltLabel without intermediate 'x' # gr1c seems to use ap-labels mainly?
    #parseablestr = ''
    parseablestr = 's'
    for plateInfo in state:
        parseablestr += str(plateInfo[0])
        i = 1
        for num in plateInfo[1]:
            parseablestr += str(num)
            i += 1
    #    parseablestr += 'x'
    #parseablestr = parseablestr[0:len(parseablestr)-1] # remove trailing 'x'
    return parseablestr

print(convertToParseableStr(initial_state))

def findPlateByLoc(state,locA):
    # first, find the plate we are moving
    checkindex = None
    for i in range(len(state)):
        plateInfo = state[i]
        if (locA == plateInfo[1]):
            checkindex = i
            break
    return checkindex

def isAbleToMove(state,pl):
    # first, find the plate we are moving
    checkindex = findPlateBySize(state,pl)
    if (checkindex is None): # if plate doesn't exist, stop (error)
        return False
    locA = state[checkindex][1]
    # make sure nothing is above us (plate must be clear overhead)
    for i in range(len(state)):
        if (i != checkindex): # skip plate that is moving
            plateInfo = state[i]
            loc = plateInfo[1]
            if (locA[0] == loc[0]): # if other-plate on same spire-rod
                if (locA[1] > loc[1]): # and if lower than other-plate
                    return False
    return True

def isLocationClear(state,locB):
    for i in range(len(state)):
        plateInfo = state[i]
        loc = plateInfo[1]
        if (locB == loc): # if other-plate is in location we want to move to
            return False
    return True

def isOpenMove(state,action):
    """
    conditions for move to be possible:
    -- plate at locA has nothing above it
    -- space at locB is free and nothing free below it and nothing above it
    """
    [pl,locA,locB] = action
    # first, find the plate we are moving
    checkindex = findPlateBySize(state,pl)
    if (checkindex is None): # if plate doesn't exist, stop (error)
        return False
    # make sure we are at locA to start
    if (locA != state[checkindex][1]): # if we aren't at required start location, stop
        return False
    # make sure nothing is above us (plate must be clear overhead)
    if (not isAbleToMove(state,pl)):
        return False
    # make sure locB is clear
    if (not isLocationClear(state,locB)):
        return False
    # make sure there is no free space below locB
    # and
    # make sure there is no filled space above locB
    platesBelow = 0
    for i in range(len(state)):
        if (i != checkindex): # skip plate that is moving
            plateInfo = state[i]
            loc = plateInfo[1]
            if (locB[0] == loc[0]): # if other-plate on same spire-rod
                if (locB[1] < loc[1]): # and if other-plate is lower
                    platesBelow += 1 # add it to the count
                if (locB[1] > loc[1]): # and if other-plate is higher than height-level moving to
                   return False # can't move there, stop immediately
    numPlatesRequiredBelow = len(state)-locB[1] # number of plates - level on spire
    # e.g., 3 plates and moving to level 3 --> requires 0 plates below
    #       3 plates and moving to level 1 --> requires 2 plates below
    if (platesBelow != numPlatesRequiredBelow):
        return False
    
    return True

def findPlateBySize(state,pl):
    # first, find the plate we are moving
    checkindex = None    
    for i in range(len(state)):
        plateInfo = state[i]
        if (pl == plateInfo[0]):
            checkindex = i
            break
    return checkindex
    
def isValidMove(state,action):
    # has to be an open move first
    if (not isOpenMove(state,action)):
        return False
    [pl,locA,locB] = action
    # first, find the plate we are moving
    checkindex = findPlateBySize(state,pl)
    #
    # all plates below have to be larger in increasing order
    #
    # grab all the plates we are dealing with
    platesOnSpire = list([[pl,locB]]) # add plate grabbing
    for i in range(len(state)):
        if (i != checkindex): # skip plate that is moving
            plateInfo = state[i]
            loc = plateInfo[1]
            if (locB[0] == loc[0]): # if other-plate on same spire-rod
                if (locB[1] < loc[1]): # and if other-plate is lower
                    platesOnSpire.append(list(plateInfo))
    #print("state = %r" % state)
    #print("action = %r" % action)
    #print("platesOnSpire = %r" % platesOnSpire)
    # sort the plates, highest to lowest
    platesSorted = []
    for i in range(len(platesOnSpire)):
        # highest height looking for this loop
        # = lowest possible height - numPlatesOnSpire + i + 1
        heightlookingfor = len(state)-len(platesOnSpire)+i+1
        # e.g., 3 - 2 + 1 = 2 then 3 - 2 + 2 = 3
        for j in range(len(platesOnSpire)): # for each plate on spire
            plateInfo = platesOnSpire[j]
            loc = plateInfo[1]
            if (loc[1] == heightlookingfor): # order by height, start at heightlookingfor
                platesSorted.append(list(plateInfo))
    #print("platesSorted = %r" % platesSorted)
    # then check to make sure that size of plates is increasing
    for i in range(len(platesOnSpire)-1):
        plateInfo = platesSorted[i]
        plateInfo2 = platesSorted[i+1]
        if (plateInfo[0]>plateInfo2[0]): # if size on top if bigger than size below
            #print("NOT valid")
            return False # then stacked top-heavy, invalid move, return False
    #print("isValid")
    return True





states2 = None


# Create a finite transition system
sys_sws2 = transys.FTS()

# can add multiple times, doesn't have to be all at once! :)
#sys_sws2.actions.add_from({'right','up','left','down'})
#sys_sws2.actions.add_from({'right2','up2','left2','down2'})

# str states
#n = 6; states2 = transys.prepend_with(range(n), 's') # this is just a list of strings...
#sys_sws2.states.add_from(set(states) ) # ...turned into a set and added...
#sys_sws2.states.initial.add_from({'s0', 's3'}) # ...and then initial state is added...

# we can do adds over and over again outwards, right?
sys_sws2.atomic_propositions.add(convertToLabel(initial_state,prepends))
sys_sws2.states.add(convertToParseableStr(initial_state),ap=convertToLabel(initial_state,prepends))
sys_sws2.states.initial.add(convertToParseableStr(initial_state))

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws2)
sys_sws2.save('test22.pdf') # show all possible transitions between states according to actions

all_locations = []
for i in range(1,3+1):
    for j in range(1,3+1):
        all_locations.append([i,j])

open_states = [list(initial_state)]
added_states = []
while (len(open_states)>0):
    workingstate = open_states.pop(0) # get next state to explore outwards
    #print("initial_state = %r" % initial_state)
    print("workingstate = %r" % workingstate)
    if workingstate not in added_states: # if we haven't expanded this state yet
        added_states.append(list(workingstate)) # add to added_states
        # and then expand this state further
        # try to move each plate one at a time:
        for pl in range(1,len(initial_state)+1): # initial state gives number of plates we start with
            # first, check if plate is moveable
            if (isAbleToMove(workingstate,pl)):
                #print("can move plate %d" % pl)
                # then, try each possible location to see if it is open to move to
                for loc in all_locations:
                    if (isLocationClear(workingstate,loc)):
                        #print("location %r is clear" % loc)
                        locB = loc
                        checkindex = findPlateBySize(workingstate,pl)
                        locA = workingstate[checkindex][1]
                        action = [pl,locA,locB]
                        # if we can move there
                        if (isOpenMove(workingstate,action)):
                        ## more restrictive: if this is a valid move according to rules
                        #if (isValidMove(workingstate,action)):
                            print("action %r is open" % action)
                            # we have a new viable state! -- update old state to new state
                            newstate = list(workingstate)
                            newstate[checkindex] = [pl,locB]
                            #print("initial_state = %r" % initial_state)
                            #print("workingstate = %r" % workingstate)
                            print("newstate is %r" % newstate)
                            if newstate not in added_states: # if not already added (previously opened)
                                #print("newstate not in added_states")
                                if newstate not in open_states: # if not waiting to be opened
                                    #print("newstate not in open_states")                                    
                                    print("adding completely new state %r !" % newstate)
                                    # add new state to explore
                                    open_states.append(list(newstate))
                                    # add new state label...
                                    sys_sws2.atomic_propositions.add(convertToLabel(newstate,prepends))
                                    # ...and new state...
                                    sys_sws2.states.add(convertToParseableStr(newstate),ap=convertToLabel(newstate,prepends))
                            # ...and transition+action from working state to new state to system
                            sys_sws2.actions.add(str(action))
                            sys_sws2.transitions.add(convertToParseableStr(workingstate),convertToParseableStr(newstate),actions=str(action))

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws2)
sys_sws2.save('test23.pdf') # show all possible transitions between states according to actions




"""

stuff below is "version 2" with pretty-printing and use of isValidMove() instead of ("just") isOpenMove()

"""

import logging
logging.basicConfig(filename='testing_stuff2.log',
                    level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)

# prepends are for pretty-printing things...
prepends = []
prepends.append('p') # plate (smallest=1, middle=2, largest=3)
prepends.append('s') # spire-rod (left=1, middle=2, right=3)
prepends.append('h') # level (highest=1, middle=2, lowest/base=3)
# assume that index 1 = plate num., index 2 = spindle-rod, index 3 = height
#initial_state = [[1,1],[1,2],[1,3]] # version 1
# or explicitly hold plate num. as first number, with position next:
#       [ [plate,[spire-rod,level]], ... ]
initial_state = [ [1,[1,1]], [2,[1,2]], [3,[1,3]] ] # version 2

# Create a finite transition system
sys_sws3 = transys.FTS()

# we can do adds over and over again outwards, right?
#sys_sws3.atomic_propositions.add(convertToAltLabel(initial_state))
#sys_sws3.states.add(convertToParseableStr2(initial_state),ap={convertToAltLabel(initial_state)})
#sys_sws3.states.initial.add(convertToParseableStr2(initial_state))
#sys_sws3.atomic_propositions.add(convertToParseableStr2(initial_state))
#sys_sws3.states.add(convertToParseableStr2(initial_state),ap={convertToParseableStr2(initial_state)})
#sys_sws3.states.initial.add(convertToParseableStr2(initial_state))
sys_sws3.states.add(convertToParseableStr2(initial_state))
sys_sws3.states.initial.add(convertToParseableStr2(initial_state))
#sys_sws3.atomic_propositions.add(convertToParseableStr2(initial_state))
#sys_sws3.states.add(convertToAltLabel(initial_state),ap=convertToParseableStr2(initial_state))
#sys_sws3.states.initial.add(convertToAltLabel(initial_state))

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws3)
sys_sws3.save('test32.pdf') # show all possible transitions between states according to actions

all_locations = []
for i in range(1,3+1):
    for j in range(1,3+1):
        all_locations.append([i,j])

open_states = [list(initial_state)]
added_states = []
while (len(open_states)>0):
    workingstate = open_states.pop(0) # get next state to explore outwards
    #print("initial_state = %r" % initial_state)
    print("workingstate = %r" % workingstate)
    if workingstate not in added_states: # if we haven't expanded this state yet
        added_states.append(list(workingstate)) # add to added_states
        # and then expand this state further
        # try to move each plate one at a time:
        for pl in range(1,len(initial_state)+1): # initial state gives number of plates we start with
            # first, check if plate is moveable
            if (isAbleToMove(workingstate,pl)):
                #print("can move plate %d" % pl)
                # then, try each possible location to see if it is open to move to
                for loc in all_locations:
                    if (isLocationClear(workingstate,loc)):
                        #print("location %r is clear" % loc)
                        locB = loc
                        checkindex = findPlateBySize(workingstate,pl)
                        locA = workingstate[checkindex][1]
                        action = [pl,locA,locB]
                        # if we can move there
                        #if (isOpenMove(workingstate,action)):
                        ## more restrictive: if this is a valid move according to rules
                        if (isValidMove(workingstate,action)):
                            print("action %r is open" % action)
                            # we have a new viable state! -- update old state to new state
                            newstate = list(workingstate)
                            newstate[checkindex] = [pl,locB]
                            #print("initial_state = %r" % initial_state)
                            #print("workingstate = %r" % workingstate)
                            print("newstate is %r" % newstate)
                            if newstate not in added_states: # if not already added (previously opened)
                                #print("newstate not in added_states")
                                if newstate not in open_states: # if not waiting to be opened
                                    #print("newstate not in open_states")                                    
                                    print("adding completely new state %r !" % newstate)
                                    # add new state to explore
                                    open_states.append(list(newstate))
                                    # add new state label...
#                                    sys_sws3.atomic_propositions.add(convertToAltLabel(newstate))
                                    #sys_sws3.atomic_propositions.add(convertToParseableStr2(newstate))
                                    # ...and new state...
#                                    sys_sws3.states.add(convertToParseableStr2(newstate),ap={convertToAltLabel(newstate)})
                                    sys_sws3.states.add(convertToParseableStr2(newstate))
                                    #sys_sws3.states.add(convertToAltLabel(newstate),ap=convertToParseableStr2(newstate))
                            # ...and transition+action from working state to new state to system
                            #sys_sws3.actions.add(str(action))
                            #sys_sws3.transitions.add(convertToParseableStr2(workingstate),convertToParseableStr2(newstate),actions=str(action))
                            sys_sws3.actions.add('a'+convertActionToStr(action))
                            sys_sws3.transitions.add(convertToParseableStr2(workingstate),convertToParseableStr2(newstate),actions='a'+convertActionToStr(action))
#                            sys_sws3.transitions.add(convertToParseableStr2(workingstate),convertToParseableStr2(newstate))
                            #sys_sws3.actions.add(str(action))
                            #sys_sws3.transitions.add(convertToAltLabel(workingstate),convertToAltLabel(newstate),actions=str(action))


# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws3)
sys_sws3.save('test33.pdf') # show all possible transitions between states according to actions

#env_safe is the same as losing?
#sys_safe is the same as an acceptable state?
#sys_prog is the goal trying to reach to win?

#
# Environment variables and specification
#
# The environment can issue a park signal that the robot just respond
# to by moving to the lower left corner of the grid.  We assume that
# the park signal is turned off infinitely often.
#
env_vars = set() # 'park'
env_init = set()                # empty set
env_prog = set() # '!park'
env_safe = set()                # empty set

# 
# System specification
#
# The system specification is that the robot should repeatedly revisit
# the upper right corner of the grid while at the same time responding
# to the park signal by visiting the lower left corner.  The LTL
# specification is given by 
#
#     []<> home && [](park -> <>lot)
#
# Since this specification is not in GR(1) form, we introduce the
# variable X0reach that is initialized to True and the specification
# [](park -> <>lot) becomes
#
#     [](X (X0reach) <-> lot || (X0reach && !park))
#

# Augment the environmental description to make it GR(1)
#! TODO: create a function to convert this type of spec automatically

# Define the specification
#! NOTE: maybe "synthesize" should infer the atomic proposition from the 
# transition system? Or, we can declare the mode variable, and the values
# of the mode variable are read from the transition system.
#

print("Writing up goals and such for system")
goal = [[1,[3,1]],[2,[3,2]],[3,[3,3]]]
print("Writing up sys vars and such for system")
#sys_init = {'X0reach'}
#sys_vars = {'Xspire3Reach'}
sys_vars = {'spire3Reach':'boolean'}
#sys_vars = {'spire3Reach'}
#sys_init = {'X0reach', 'sys_actions = right'}
action = [1,[1,1],[3,3]]
#sys_init = {'spire3Reach', 'sys_actions = "%s"' % convertActionToStr(action)}
#sys_init = {'Xspire3Reach', 'sys_actions = %s' % convertActionToStr(action)}
sys_init = {'spire3Reach'}
#sys_prog = {'lot'}               # []<>lot
#goalStr = str(convertToAltLabel(goal))
#sys_sws3.atomic_propositions.add(convertToAltLabel(goal))
#sys_sws3.states.add(convertToParseableStr2(goal),ap={convertToAltLabel(goal)})
goalStr = str(convertToParseableStr2(goal))
#sys_sws3.atomic_propositions.add(convertToParseableStr2(goal))
#sys_sws3.states.add(convertToParseableStr2(goal),ap={convertToParseableStr2(goal)})
sys_sws3.states.add(convertToParseableStr2(goal))
#goalStr = str(convertToParseableStr2(goal))
print(goalStr)
#sys_prog = {goalStr} #sys_prog = {'131232333'}               # []<> (stuff-stakced-on-spire)
sys_prog = {'loc=%s' % goalStr} #sys_prog = {'131232333'}               # []<> (stuff-stakced-on-spire)
#sys_prog = {str(convertToParseableStr2(goal))} #sys_prog = {'131232333'}               # []<> (stuff-stakced-on-spire)
#sys_safe = {'X (X0reach) <-> lot'}
#sys_safe = {'X (spire3Reach) <-> "%s"' % goalStr} # 1-3-1_2-3-2_3-3-3
#sys_safe = {'X (spire3Reach) <-> %s' % goalStr} # 1-3-1_2-3-2_3-3-3
sys_safe = {'X (spire3Reach) <-> loc=%s' % goalStr} # 1-3-1_2-3-2_3-3-3
print(sys_safe)
#sys_safe = {'X (spire3Reach) <-> ' + str(convertToParseableStr2(goal))} #sys_safe = {'X (spire3Reach) <-> 131232333'}
sys_prog |= {'spire3Reach'}

print("Creating spec for sys_sw3 system")

# Create the specification
#specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
#                    env_safe, sys_safe, env_prog, sys_prog)
specs = spec.GRSpec(env_vars=env_vars, sys_vars=sys_vars,
                    sys_init=sys_init, sys_safety=sys_safe,
                    env_prog=env_prog, sys_prog=sys_prog)
                    
print("Done creating spec for sys_sw3 system")

# Controller synthesis
#
# At this point we can synthesize the controller using one of the available
# methods.  Here we make use of JTLV.
#
print("Synthesizing solution for sys_sw3 system")
#ctrl = synth.synthesize('jtlv', specs, sys=sys_sws3) # see: https://github.com/tulip-control/tulip-control/issues/98 (big integers, need for ="right" in sys_init...)
# jtlv: still doesn't like actions 'a23213' etc. currently...
ctrl = synth.synthesize('gr1c', specs, sys=sys_sws3)
# gr1c: error on line 2, unexpected NUMBER -- doesn't want goalStr to look like a number (added 's' to front as a workaround...)
# gr1c: error on line 9, unexpected -blah- or NUMBER -- this thing does "24" and "6" without "loc = " in specs stuff apparently(?)
print("Done synthesizing solution for sys_sw3 system")

print("Creating .png file for sys_sw3 system")
# Generate a graphical representation of the controller for viewing
if not ctrl.save('testing_stuff2_sws3.png'):
    print("Couldn't save .png file, printing ctrl instead")
    print(ctrl)
    print("Done printing ctrl instead")
print("Done creating .png file for sys_sw3 system")







"""
sys_sws.atomic_propositions.add_from(['home','lot'])
state_labels = [{'home'}, set(), set(), set(), set(), {'lot'}]

# Add states and decorate TS with state labels (aka atomic propositions)
for state, label in zip(states, state_labels):
    sys_sws.states.add(state, ap=label)

# mode1 transitions
transmat1 = np.array([[0,1,0,0,1,0],
                      [0,0,1,0,0,1],
                      [0,0,1,0,0,0],
                      [0,1,0,0,1,0],
                      [0,0,1,0,0,1],
                      [0,0,0,0,0,1]])
sys_sws.transitions.add_adj(
    sp.lil_matrix(transmat1), states, actions='right'
)
# for OpenFTS(), sys_actions='' and env_actions='' defined for add_adj()
# see: hybrid.py
                      
# mode2 transitions
transmat2 = np.array([[0,0,0,1,0,0],
                      [0,0,0,0,1,1],
                      [0,0,0,0,0,1],
                      [0,0,0,1,0,0],
                      [0,0,0,0,1,0],
                      [0,0,0,0,0,1]])
sys_sws.transitions.add_adj(
    sp.lil_matrix(transmat2), states, actions='up'
)
                      
# mode3 transitions
transmat3 = np.array([[1,0,0,0,0,0],
                      [1,0,0,1,0,0],
                      [0,1,0,0,1,0],
                      [0,0,0,1,0,0],
                      [1,0,0,1,0,0],
                      [0,1,0,0,1,0]])
sys_sws.transitions.add_adj(
    sp.lil_matrix(transmat3), states, actions='left'
)
                      
# mode4 transitions
transmat4 = np.array([[1,0,0,0,0,0],
                      [0,1,0,0,0,0],
                      [0,0,1,0,0,0],
                      [1,0,0,0,0,0],
                      [0,1,1,0,0,0],
                      [0,0,1,0,0,0]])
sys_sws.transitions.add_adj(
    sp.lil_matrix(transmat4), states, actions='down'
)

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws)
sys_sws.save('test.pdf') # show all possible transitions between states according to actions

#
# Environment variables and specification
#
# The environment can issue a park signal that the robot just respond
# to by moving to the lower left corner of the grid.  We assume that
# the park signal is turned off infinitely often.
#
#env_vars = {'park'}
#env_init = set()                # empty set
#env_prog = {'!park'}
#env_safe = set()                # empty set
env_vars = set()
env_init = set()                # empty set
env_prog = set()
env_safe = set()                # empty set

# 
# System specification
#
# The system specification is that the robot should repeatedly revisit
# the upper right corner of the grid while at the same time responding
# to the park signal by visiting the lower left corner.  The LTL
# specification is given by 
#
#     []<> home && [](park -> <>lot)
#
# Since this specification is not in GR(1) form, we introduce the
# variable X0reach that is initialized to True and the specification
# [](park -> <>lot) becomes
#
#     [](X (X0reach) <-> lot || (X0reach && !park))
#

# Augment the environmental description to make it GR(1)
#! TODO: create a function to convert this type of spec automatically

# Define the specification
#! NOTE: maybe "synthesize" should infer the atomic proposition from the 
# transition system? Or, we can declare the mode variable, and the values
# of the mode variable are read from the transition system.
#
#sys_vars = {'X0reach'}
#sys_init = {'X0reach', 'sys_actions = right'}
#sys_prog = {'home'}               # []<>home
#sys_safe = {'X (X0reach) <-> lot || (X0reach && !park)'}
#sys_prog |= {'X0reach'}
#
#sys_vars = {'X0reach'}
#sys_init = {'X0reach', 'sys_actions = right'}
#sys_prog = {'home'}               # []<>home
#sys_safe = {'X (X0reach) <-> lot'}
#sys_prog |= {'X0reach'}
#
sys_vars = {'X0reach'}
sys_init = {'X0reach', 'sys_actions = right'}
sys_prog = {'lot'}               # []<>lot
# && [](lot -> []lot) # once at lot, stay in lot?
#sys_safe = {'X (X0reach) <-> lot || (X0reach && lot)'}
sys_safe = {'X (X0reach) <-> lot'}
sys_prog |= {'X0reach'}

# Create the specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)
                    
# Controller synthesis
#
# At this point we can synthesize the controller using one of the available
# methods.  Here we make use of JTLV.
#
#ctrl = synth.synthesize('jtlv', specs, sys=sys_sws)
ctrl = synth.synthesize('gr1c', specs, sys=sys_sws)

# Generate a graphical representation of the controller for viewing
if not ctrl.save('controlled_switching.png'):
    print(ctrl)
"""