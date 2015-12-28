# Contains code relating to goal decomposition and mental model projection
import dash  # don't import specific names so this module will be compiled first

goalWeightDict = dict()
goalRequirementsDict = dict()
knownDict = dict()

# Read the agent definition in a simpler syntax and create the appropriate definitions
traceLoad = False
def readAgent(string):
    state = 0
    goalRequirements = 1
    lines = []
    for line in string.split('\n'):
        line = line.strip()
        if state == goalRequirements:
            if line == "":
                readGoalRequirements(lines)
                state = 0
            else:
                lines.append(line)
        elif line.startswith("goalWeight"):
            readGoalWeight(line)
        elif line.startswith("goalRequirements"):
            state = goalRequirements
            lines = [line]
        elif line.startswith("known"):
            readKnown(line)

def readGoalWeight(line):
    # line has form 'goalWeight predicate(arg1, arg2, ..) integer'
    goal = readGoalTuple(line[line.find(" "):].strip())
    weight = int(line[line.find(")") + 1:].strip())
    goalWeight(goal, weight)

def readGoalRequirements(lines):
    goal = readGoalTuple(lines[0][lines[0].find(" "):].strip())
    requirements = [readGoalTuple(line) for line in lines[1:]]
    if traceLoad: print "Adding goal requirements for", goal, ":", requirements
    goalRequirements(goal, requirements)

def readKnown(line):
    goal = readGoalTuple(line[line.find(" "):].strip())
    knownTuple(goal)

# Read a goal as a tuple from the line, which should start with the goal description
def readGoalTuple(line):
    predicate = line[0:line.find("(")].split(" ")[0]
    args = line[line.find("(")+1:line.find(")")].split(", ")
    return tuple([predicate]+args)
    

def goalWeight(goal, weight):
    goalWeightDict[goal] = weight

def goalRequirements(goal, requirements):
    # Treat as append, index by goal name (head)
    # and collate the goal itself with the body
    if goal[0] not in goalRequirementsDict:
        goalRequirementsDict[goal[0]] = []
    goalRequirementsDict[goal[0]].append((goal, requirements))

def printGoals():
    for goal in goalWeightDict:
        print goal, goalWeightDict[goal]

traceKnown = False

def knownTuple(t):
    known(t[0],t[1:])

# Adds 'goal' as a known fact or completed goal
def known(predicate, arguments):
    if predicate not in knownDict:
        knownDict[predicate] = []
    goal = tuple([predicate]) + tuple(arguments)  # this allows arguments to be any iterable
    if goal not in knownDict[predicate]:
        if traceKnown: print "Recording as known", goal
        knownDict[predicate].append(goal)

# Might be subgoal or top-level goal
def isGoal(goal):
    return goal[0] in goalRequirementsDict

def chooseAction():
    return chooseActionForGoals([chooseGoal()])

def chooseGoal():
    if goalWeightDict == {}:
        return None
    # Return a goal with highest weight
    return max(goalWeightDict.items(), key = lambda pair: pair[1])[0]

# indent is used to print trace information with increasing indentation
traceGoals = False
def chooseActionForGoals(goals, indent=0):
    if goals == None:
        return None
    if traceGoals: print ' '*indent, "Seeking action for goals", goals
    gpb = findGoalRequirements(goals[0])
    if gpb == None:
        print "No goal requirements match for ", goals[0]
        return None
    (goal, requirements, bindings) = gpb
    # Return the first action in the requirements body, substituting bindings
    return nextAction(goal, requirements, bindings, indent)

# Recursively move through subgoals and return the next primitive action
def nextAction(goal, requirements, bindings, indent):
    for candidate in requirements[1]:
        subbed = substitute(candidate, bindings)
        if traceGoals: print ' '*indent, "inspecting requirement", subbed, "from", candidate
        newBindings = isKnown(subbed)
        if newBindings != False:
            if traceGoals: print ' '*indent, candidate, "known with bindings", newBindings
            bindings = dict(bindings.items() + newBindings.items())  # wasteful but succinct
            continue
        elif dash.isPrimitive(candidate):
            if traceGoals: print ' '*indent, "returning primitive", subbed
            return subbed
        elif isGoal(candidate):
            action = chooseActionForGoals([subbed], indent + 2)
            if action != None and action[0] == 'known':  
                # This subgoal was achievable from what is already done.
                # Update bindings
                if traceGoals: print ' '*indent, candidate, "already achieved"
                bindings = dict(bindings.items() + action[1].items())
                continue
            else:
                return action
        else:   # Not adding 'executables' right now
            print ' '*indent, subbed, "is not a goal or primitive or already known"
            return None
    # If we got here, then we went through all the subactions without needing to do anything,
    # So the goal should be marked as achieved
    knownTuple(substitute(goal,bindings))
    if traceGoals: print "Marking", substitute(goal,bindings), "as achieved"
    return ['known', bindings]
    

# Known kind of conflates other ways of knowing things with knowing that a
# subgoal has been performed
def isKnown(goal):
    if goal[0] in knownDict:
        for term in knownDict[goal[0]]:
            bindings = unify(goal[1:], term[1:])
            if bindings != False:  # Since {} means success with no new bindings
                return bindings
    return False

def findGoalRequirements(goal):
    if goal[0] in goalRequirementsDict:
        for pair in goalRequirementsDict[goal[0]]:
            bindings = unifyGoal(goal, pair)
            if bindings != None:
                return (goal, pair, bindings)
    else:
        return None

# Attempt to find a mapping for the variables that works
def unifyGoal(goal, pair):
    # Double-check the goal predicate matches, although it should be construction
    # and also check length of goal and goal requirements head.
    head = pair[0]
    if goal[0] != head[0] or len(goal) != len(head):
        return None
    return unify(goal[1:], head[1:])

def unify(pattern, candidate):
    bindings = {}
    # Match the arguments in the goal and the requirements head
    for (goalarg, matcharg) in zip(pattern, candidate):
        if isConstant(matcharg):
            if isConstant(goalarg):
                if matcharg != goalarg: # constants must match
                    return False
            elif goalarg in bindings:
                if matcharg != bindings[goalarg]:  # assume bound to another constant
                    return False
            else:
                bindings[goalarg] = matcharg
        elif matcharg not in bindings: # free variable
            bindings[matcharg] = goalarg
        elif goalarg != bindings[matcharg]:
            return False
    # Just match the head for now
    return bindings

def isConstant(term):
    # Anything other than a string is assumed to be a constant
    # This test assumes python 2.x
    return not isinstance(term, basestring) or term.startswith("!")

# Substitute bindings in tuple representation of a term,
# where the first argument is the predicate.
def substitute(predicate, bindings):
    args = [arg if arg not in bindings else bindings[arg] for arg in predicate[1:]]
    args.insert(0,predicate[0])
    return tuple(args)

