import system1
from system2 import goalWeight, goalRequirements, printGoals, knownTuple, known, substitute, chooseAction, readAgent, isConstant, isKnown

primitiveActionDict = dict()

# This is in the java part in the old agent
def agentLoop(maxIterations=-1):
    nextAction = chooseAction()
    iteration = 0
    while nextAction != None and (maxIterations < 0 or iteration < maxIterations):
        print "Next action is ", nextAction
        result = performAction(nextAction)
        updateBeliefs(result, nextAction)
        nextAction = chooseAction()
        iteration += 1
    if nextAction == None:
        print "No action chosen"
    elif maxIterations >= 0 and iteration >= maxIterations:
        print "Finished finite agent cycles:", maxIterations, "with", iteration

def do():
    # Skipping the other pieces for now,
    # and the breakdown will probably change as the
    # agent structure is simplified from DASH 1.
    return chooseAction()


def primitiveActions(l):
    # Add the items into the set of known primitive actions
    # mapping name to function
    for item in l:
        primitiveActionDict[item[0]] = item[1]

def isPrimitive(goal):
    return goal[0] in primitiveActionDict

def performAction(action):
    if isPrimitive(action):
        return primitiveActionDict[action[0]](action)

def updateBeliefs(result, action):
    print "Updating beliefs based on action", action, "with result", result
    if isinstance(result, list):
        for bindings in result:
            knownTuple(substitute(action, bindings))   # Mark action as performed/known
