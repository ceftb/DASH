import system1
from system2 import goalWeight, goalRequirements, printGoals, knownTuple, knownFalseTuple, known, substitute, chooseAction, readAgent, isConstant, isKnown, preferPlan

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


def primitiveActions(l):
    # Add the items into the set of known primitive actions
    # mapping name to function
    for item in l:
        if isinstance(item, basestring):
            primitiveActionDict[item] = item # store the name and look for the function at planning time
        else:
            primitiveActionDict[item[0]] = item[1]


def isPrimitive(goal):
    return goal[0] in primitiveActionDict


def performAction(action):
    if isPrimitive(action):
        function = primitiveActionDict[action[0]]
        return function(action)

traceUpdate = False


def updateBeliefs(result, action):
    if traceUpdate:
        print "Updating beliefs based on action", action, "with result", result
    if not result:
        knownFalseTuple(action)
    if isinstance(result, list):
        for bindings in result:
            concreteResult = substitute(action, bindings)
            knownTuple(concreteResult)   # Mark action as performed/known
            knownTuple(('performed', concreteResult))   # Adding both lets both idioms be used in the agent code.
