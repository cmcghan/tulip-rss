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
-- initial commit, 2015-08-10 CLRM

=== Summary of contents ===
...
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
    labelstr = ''
    i = int(0)
    for row in holdgrid:
        i += 1
        for j in row:
            labelstr += str(j) #+ ' '
        #labelstr = str(labelstr[0:len(str(labelstr))-1]) # remove trailing ' '
        # add one more '\' in front of the 'n' each time we '\n' <-- *** NOTE, THIS IS VERY BRITTLE 'PRETTY PRINTING'!
        if (i < len(holdgrid)): # don't put a '\\\...\n' on the last line
            if i == 1:
                labelstr += '\n'
            elif i%2 == 0: # i even
                labelstr += '\\'*(i/2) + 'n'
            else: # i odd
                labelstr += '\\'*(i/2) + '\n'
    #labelstr = labelstr[0:len(labelstr)-1] # remove trailing '\n'
    labelstr = '{' + str(labelstr) + '}' # add leading '{' and trailing '}'
    
    labelstr5 = str(holdgrid[0][0]) + str(holdgrid[0][1]) + str(holdgrid[0][2]) + str(holdgrid[1][0]) + str(holdgrid[1][1]) + str(holdgrid[1][2]) + str(holdgrid[2][0]) + str(holdgrid[2][1]) + str(holdgrid[2][2])
    
    return labelstr5

def convertToAltLabelSet(state):
    # state is [[pl=1, [sp,lv]], [pl=2, [sp,lv]], [pl=3, [sp,lv]]]
    newset = set()
    #parseablestr = ''
    for plateInfo in state:
        parseablestr = 'pl' + str(plateInfo[0])
#        i = 1
#        for num in plateInfo[1]:
#            parseablestr += '-' + str(num)
#            i += 1
        newset.add( parseablestr + 'sp' + str(plateInfo[1][0]) ) # adds 'pl#sp#'
        newset.add( parseablestr + 'lv' + str(plateInfo[1][1]) ) # adds 'pl#lv#'
    
    return newset

def convertToAltLabelSet2(state):
    # state is [[pl=1, [sp,lv]], [pl=2, [sp,lv]], [pl=3, [sp,lv]]]
    newset = set()
    #parseablestr = ''
    for plateInfo in state:
        parseablestr = 'pl' + str(plateInfo[0])
#        i = 1
#        for num in plateInfo[1]:
#            parseablestr += '-' + str(num)
#            i += 1
        #newset.add( parseablestr + 'sp=' + str(plateInfo[1][0]-1) ) # adds 'pl#sp=#' but shifted 1 down (for 0-2 instead of (1-3))
        #newset.add( parseablestr + 'lv=' + str(plateInfo[1][1]-1) ) # adds 'pl#lv=#' but shifted 1 down (for 0-2 instead of (1-3))
        # added 1 to end of sys_vars and removed shift -- sys_vars seems to not want to use/expose the 0 value?        
        newset.add( parseablestr + 'sp=' + str(plateInfo[1][0]) ) # adds 'pl#sp=#' (1-3)
        newset.add( parseablestr + 'lv=' + str(plateInfo[1][1]) ) # adds 'pl#lv=#' (1-3)
    
    return newset

def convertToAltLabelSet3Str(state):
    # state is [[pl=1, [sp,lv]], [pl=2, [sp,lv]], [pl=3, [sp,lv]]]
    newstring = ''
    newSet = convertToAltLabelSet2(state)
    #parseablestr = ''
    for piece in newSet:
        newstring += str(piece) + ' && '  # adds 'pl#sp=#' # use & not && or ^ ?
    newstring = newstring[0:len(newstring)-4] # remove trailing ' && '
    return newstring

def convertActionToStr(action): # [pl,[spa,lva],[spb,lvb]]
    return str(action[0])+str(action[1][0])+str(action[1][1])+str(action[2][0])+str(action[2][1])
    
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


"""

stuff below is "version 2" with pretty-printing and use of isOpenMove() instead of ("just") isValidMove()

"""

import logging
logging.basicConfig(filename='tower_of_hanoi3.log',
                    level=logging.INFO, filemode='w') # level=logging.DEBUG
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
#initset = convertToAltLabelSet(initial_state)
#sys_sws3.atomic_propositions.add_from(list(initset))
#sys_sws3.states.add(convertToParseableStr2(initial_state),ap=initset)
sys_sws3.states.add(convertToParseableStr2(initial_state))
sys_sws3.states.initial.add(convertToParseableStr2(initial_state))

sys_safe = set()
initset3str = convertToAltLabelSet3Str(initial_state)
#sys_safe = { str(initset3str) + ' <-> ' + 'loc=' + str(convertToParseableStr2(initial_state)) } # initializing sys_safe...
#sys_safe = { '(' + str(initset3str) + ') <-> ' + 'loc=' + str(convertToParseableStr2(initial_state)) } # initializing sys_safe...
#sys_safe = { 'X((loc=' + str(convertToParseableStr2(initial_state)) + ') -> (' + str(initset3str) + '))' } # initializing sys_safe...  # this is what the stuff seems to look like for some other known-working things from gr1c
sys_safe = { '(loc=' + str(convertToParseableStr2(initial_state)) + ') <-> (' + str(initset3str) + ')' } # initializing sys_safe...  # this is what the stuff seems to look like for some other known-working things from gr1c
#sys_safe = { '(loc=' + str(convertToParseableStr2(initial_state)) + ') -> (' + str(initset3str) + ')' } # initializing sys_safe...

all_locations = []
for i in range(1,3+1):
    for j in range(1,3+1):
        all_locations.append([i,j])

open_states = [list(initial_state)]
added_states = []
while (len(open_states)>0):
    workingstate = open_states.pop(0) # get next state to explore outwards
    if workingstate not in added_states: # if we haven't expanded this state yet
        added_states.append(list(workingstate)) # add to added_states
        # and then expand this state further
        # try to move each plate one at a time:
        for pl in range(1,len(initial_state)+1): # initial state gives number of plates we start with
            # first, check if plate is moveable
            if (isAbleToMove(workingstate,pl)):
                # then, try each possible location to see if it is open to move to
                for loc in all_locations:
                    addthisflag = 0 # zero out flag to start with
                    locB = loc
                    checkindex = findPlateBySize(workingstate,pl)
                    locA = workingstate[checkindex][1]
                    newstate = list(workingstate)
                    newstate[checkindex] = [pl,locB] # updating "newstate" with single-plate move
                    action = [pl,locA,locB]
                    # if attempt to stay in same state... (this is fine/valid)
                    if (newstate == workingstate):
                        addthisflag = 1
                    # else, check if location is clear
                    elif (isLocationClear(workingstate,loc)):
#                        locB = loc
#                        checkindex = findPlateBySize(workingstate,pl)
#                        locA = workingstate[checkindex][1]
#                        action = [pl,locA,locB]
                        # if we can move there
                        if (isOpenMove(workingstate,action)):
                        ## more restrictive: if this is a valid move according to rules
                        #if (isValidMove(workingstate,action)):
                            # we have a new viable state! -- update old state to new state
#                            newstate = list(workingstate)
#                            newstate[checkindex] = [pl,locB]
                            addthisflag = 1
                    else:
                        #addthisflag = 0
                        pass
                    if (addthisflag == 1): # case marked for addition to sets of variables/states/actions/transitions
                        if newstate not in added_states: # if not already added (previously opened)
                            #print("newstate not in added_states")
                            if newstate not in open_states: # if not waiting to be opened
                                # add new state to explore
                                open_states.append(list(newstate))
                                # add new state label...
                                #newset = convertToAltLabelSet(newstate)
#                                    sys_sws3.atomic_propositions.add(newset) # can add, but can't hash during synthesis?
                                #sys_sws3.atomic_propositions.add_from(list(newset))
                                # ...and new state...
#                                    sys_sws3.states.add(convertToParseableStr2(newstate),ap={convertToAltLabel(newstate)})
#                                    sys_sws3.states.add(convertToParseableStr2(newstate))
                                #sys_sws3.states.add(convertToParseableStr2(newstate),ap=newset)
                                sys_sws3.states.add(convertToParseableStr2(newstate))
                                newset3str = convertToAltLabelSet3Str(newstate)
                                #sys_safe |= { str(newset3str) + ' <-> ' + 'loc=' + str(convertToParseableStr2(newstate))}
                                #sys_safe |= { '(' + str(newset3str) + ') <-> ' + 'loc=' + str(convertToParseableStr2(newstate))}
#                                sys_safe |= { 'X((loc=' + str(convertToParseableStr2(newstate)) + ') -> (' + str(newset3str) + '))' } # this gives error "ValueError: key: pl2lv, cannot be assigned value: 4 Admissible values are: set([0, 1, 2])"
                                sys_safe |= { '(loc=' + str(convertToParseableStr2(newstate)) + ') <-> (' + str(newset3str) + ')' } # this gives error "ValueError: key: pl2lv, cannot be assigned value: 4 Admissible values are: set([0, 1, 2])"
                                #sys_safe |= { 'X((loc=' + str(convertToParseableStr2(newstate)) + ') -> (' + str(newset3str) + '))' } # this is what the stuff seems to look like for some other known-working things from gr1c
                                #sys_safe |= { '(loc=' + str(convertToParseableStr2(newstate)) + ') -> (' + str(newset3str) + ')' }
#                                    sys_sws3.states.add(convertToParseableStr2(newstate),ap=newset) # wants PowerSet(MathSet(set([])))
                        # ...and transition+action from working state to new state to system
                        sys_sws3.actions.add('a'+convertActionToStr(action))
                        sys_sws3.transitions.add(convertToParseableStr2(workingstate),convertToParseableStr2(newstate),actions='a'+convertActionToStr(action))

# This is what is visible to the outside world (and will go into synthesis method)
print(sys_sws3)
sys_sws3.save('hanoi3.pdf') # show all possible transitions between states according to actions

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
# The system specification is that the robot should (repeatedly?) revisit
# the rightmost spire (this is because there are no 'wait' or 'stay in same
# state' actions currently).

# Augment the environmental description to make it GR(1)
#! TODO: create a function to convert this type of spec automatically

# Define the specification
#! NOTE: maybe "synthesize" should infer the atomic proposition from the 
# transition system? Or, we can declare the mode variable, and the values
# of the mode variable are read from the transition system.
#

print("Writing up goals and such for system")
goal = [[1,[3,1]],[2,[3,2]],[3,[3,3]]]
goal2 = [[1,[2,3]],[2,[1,2]],[3,[1,3]]]
print("Writing up sys vars and such for system")
sys_vars = {'spire3Reach':'boolean'}
#sys_vars.update({'pl1sp':(0,2)}) # note: for gr1c, lower bound must be zero (0)
#sys_vars.update({'pl2sp':(0,2)}) # apparently, with not too many things in sys_safe (set+below), get a "ValueError: key: pl2lv, cannot be assigned value: 4 Admissible values are: set([0, 1, 2])"
#sys_vars.update({'pl3sp':(0,2)}) # so comment these out and try them solo without the atomic propositions (b/c they might be remapping variable names?)
#sys_vars.update({'pl1lv':(0,2)})
#sys_vars.update({'pl2lv':(0,2)})
#sys_vars.update({'pl3lv':(0,2)})

# does sys_vars actually use the "0" value? it doesn't seem to...
# basically, looks like a "0" value pulls the value completely off the stack (as False?), in the 'atomic proposition' sense of things
# so, we want to avoid using value=0 for this kind of stuff! ^_^
sys_vars.update({'pl1sp':(0,3)}) # note: for gr1c, lower bound must be zero (0)
sys_vars.update({'pl2sp':(0,3)}) # apparently, with not too many things in sys_safe (set+below), get a "ValueError: key: pl2lv, cannot be assigned value: 4 Admissible values are: set([0, 1, 2])"
sys_vars.update({'pl3sp':(0,3)}) # so comment these out and try them solo without the atomic propositions (b/c they might be remapping variable names?)
sys_vars.update({'pl1lv':(0,3)})
sys_vars.update({'pl2lv':(0,3)})
sys_vars.update({'pl3lv':(0,3)})

#sys_vars = set()
#sys_init = {'spire3Reach'}
sys_init = set()
goalStr = str(convertToParseableStr2(goal))
#goalStr = str(convertToParseableStr2(goal2))
#sys_sws3.states.add(goalStr)
##sys_prog = {goalStr} #sys_prog = {'131232333'}               # []<> (stuff-stakced-on-spire)
sys_prog = {'loc=%s' % goalStr} #sys_prog = {'131232333'}               # []<> (stuff-stakced-on-spire)
##sys_safe = {'X (spire3Reach) <-> %s' % goalStr} # 1-3-1_2-3-2_3-3-3
#sys_safe = {'X (spire3Reach) <-> loc=%s' % goalStr} # 1-3-1_2-3-2_3-3-3
#sys_safe = set()
#sys_safe = {'spire3Reach <-> loc=%s' % goalStr} # 1-3-1_2-3-2_3-3-3
sys_safe |= {'spire3Reach <-> loc=%s' % goalStr} # 1-3-1_2-3-2_3-3-3
#sys_prog |= {'spire3Reach'}
# below is constraint on making sure bigger disks do not sit on top of smaller disks... for use with isOpenMove() over more-restrictive isValidMove()
# requires that checks were done previously to make sure that (a) disk is on top of spire (open air above it), (b) 
#checkstring  = '( ((pl1sp != pl2sp) && (pl2sp != pl3sp) && (pl1sp != pl2sp)) || ' # no disks on same spire, or...
#checkstring += '( ((pl1sp = pl2sp) && (pl1sp != pl3sp) && (pl1lv < pl2lv)) || ((pl2sp = pl3sp) && (pl1sp != pl3sp) && (pl2lv < pl3lv)) || ((pl1sp = pl3sp) && (pl1sp != pl2sp) && (pl1lv < pl3lv)) ) || ' # if (only) two disks on same spire then smaller disk higher than larger disk, or...
#checkstring += '((pl1sp = pl2sp) && (pl2sp = pl3sp) && (pl1sp = pl2sp) && (pl1lv < pl2lv) && (pl2lv < pl3lv)) )' # if all three dissk on same spire, each smaller disk higher than larger disk
#sys_safe |= {'(pl1sp != 4 )'} # okay to compare variable to number...
#sys_safe |= {'( (pl1sp != pl2sp) && (pl2sp != pl3sp) && (pl1sp != pl3sp) && (pl1sp != 4) )'} # ...but variable-to-variable doesn't seem to work???, causes error "syntax error, unexpected VARIABLE, expecting NUMBER Error detected on line 14."
#sys_safe |= {'((pl1sp != pl2sp) && (pl2sp != pl3sp) && (pl1sp != pl2sp))'}
#sys_safe |= {'%s' % checkstring}
#sys_safe |= {'%s -> X(%s)' % (checkstring,checkstring)}
#sys_safe |= {'((pl2sp = 0) && (pl3sp = 0))'} # gr1c solves for goal2 case
#sys_safe |= {'((pl2sp = 1) && (pl3sp = 1))'} # gr1c gives error 255
#sys_safe |= {'(pl2sp = pl3sp)'} # gr1c gives syntax error ""syntax error, unexpected VARIABLE, expecting NUMBER" line 25
#sys_safe |= {'(pl2lv < pl3lv)'} # gr1c gives syntax error "syntax error, unexpected VARIABLE, expecting NUMBER" line 18
#sys_safe |= {'(pl2lv != pl3lv)'} # gr1c gives syntax error "syntax error, unexpected VARIABLE, expecting NUMBER" line 26

# this constraint when used with either isValidMove() or the larger set of states from isOpenMove() still gives a good solution
# note that isOpenMove() still restricts the 'valid state space' we are searching over according to a couple conditions, namely:
# -- plate move-action corresponds to locA (current position of plate to-be-moved)
# -- plate at locA has nothing above it
# -- space at locB is free and nothing free below it and nothing above it
checkstring = '('
#lo=0
#hi=3
lo=1
hi=4
for i in range(lo,hi):
    for j in range(lo,hi):
        for k in range(lo,hi):
            if (i!=j) and (j!=k) and (i!=k): # no disks on same spire... or
                checkstring += '((pl1sp = %d) && (pl2sp = %d) && (pl3sp = %d)) || ' % (i,j,k)
            if (i==j) and (j!=k): # if (only) two disks on same spire then smaller disk higher than larger disk, or...
                for ii in range(lo,hi):
                    for jj in range(lo,hi):
                        if (ii<jj):
                            checkstring += '((pl1sp = %d) && (pl2sp = %d) && (pl3sp = %d) && (pl1lv = %d) && (pl2lv = %d)) || ' % (i,j,k,ii,jj)
            if (j==k) and (i!=j): # if (only) two disks on same spire then smaller disk higher than larger disk, or...
                for jj in range(lo,hi):
                    for kk in range(lo,hi):
                        if (jj<kk):
                            checkstring += '((pl1sp = %d) && (pl2sp = %d) && (pl3sp = %d) && (pl2lv = %d) && (pl3lv = %d)) || ' % (i,j,k,jj,kk)
            if (i==k) and (i!=j): # if (only) two disks on same spire then smaller disk higher than larger disk, or...
                for ii in range(lo,hi):
                    for kk in range(lo,hi):
                        if (ii<kk):
                            checkstring += '((pl1sp = %d) && (pl2sp = %d) && (pl3sp = %d) && (pl1lv = %d) && (pl3lv = %d)) || ' % (i,j,k,ii,kk)
            if (i==j) and (j==k) and (i==k): # if all three disks on same spire, each smaller disk higher than larger disk
                for ii in range(lo,hi):
                    for jj in range(lo,hi):
                        for kk in range(lo,hi):
                            if (ii<jj) and (jj<kk):
                                checkstring += '((pl1sp = %d) && (pl2sp = %d) && (pl3sp = %d) && (pl1lv = %d) && (pl2lv = %d) && (pl3lv = %d)) || ' % (i,j,k,ii,jj,kk)
checkstring = checkstring[0:len(checkstring)-4] # remove trailing ' || '
checkstring += ')'
sys_safe |= {'%s' % checkstring} # or sys_safe = {checkstring} which also works, whichever...

print("Creating spec for sys_sw3 system")

# Create the specification
#specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
#                    env_safe, sys_safe, env_prog, sys_prog)
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
# gr1c: error on line 9, unexpected -blah- or NUMBER -- this thing does "24" and "6" without "loc=" in specs stuff apparently(?)
print("Done synthesizing solution for sys_sw3 system")

print("Creating .png file for sys_sw3 system")
# Generate a graphical representation of the controller for viewing
if not ctrl.save('hanoi3_sws3.png'):
    print("Couldn't save .png file, printing ctrl instead")
    print(ctrl)
    print("Done printing ctrl instead")
print("Done creating .png file for sys_sw3 system")
