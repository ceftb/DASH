# Contains code relating to goal decomposition and mental model projection
import dash  # don't import specific names so this module will be compiled first
import compiler # Testing using the compiler to parse expressions

goalWeightDict = dict()
goalRequirementsDict = dict()
knownDict = dict()
projectionRuleDict = dict()

# Read the agent definition in a simpler syntax and create the appropriate definitions
traceLoad = False
def readAgent(string):
    # state is used for multi-line statements like goalRequirements
    # and projection rules
    state = 0
    goalRequirements = 1
    project = 2
    lines = []
    for line in string.split('\n'):
        if "#" in line:
            line = line[0:line.find("#")]
        line = line.strip()
        if state == goalRequirements or state == project:
            if line == "":
                if state == goalRequirements:
                    readGoalRequirements(lines)
                elif state == project:
                    readProject(lines)
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
        elif line.startswith("primitive"):
            readPrimitive(line)
        elif line.startswith("project"):
            state = project
            lines = [line]

def readGoalWeight(line):
    # line has form 'goalWeight predicate(arg1, arg2, ..) integer'
    goal = readGoalTuple(line[line.find(" "):line.rfind(" ")].strip())
    weight = int(line[line.rfind(" "):].strip())
    print "Goal is ", goal
    goalWeight(goal, weight)

def readGoalRequirements(lines):
    goal = readGoalTuple(lines[0][lines[0].find(" "):].strip())
    requirements = [readGoalTuple(line) for line in lines[1:]]
    if traceLoad: print "Adding goal requirements for", goal, ":", requirements
    goalRequirements(goal, requirements)

def readKnown(line):
    goal = readGoalTuple(line[line.find(" "):].strip())
    knownTuple(goal)

# Read a goal as a tuple from the line, which should start with the goal 
# description, e.g. goal(arg1, arg2, ..). Each arg may be a subgoal.
# Uses the python compiler's parser
def readGoalTuple(line):
    # It's a compiler module, with a statement node with one Discard object
    return parseToTuple(compiler.parse(line).node.nodes[0].expr)

# It's tempting to leave the parse tree with the classes from the compiler
# module but I'd like to make it modular with abstraction
def parseToTuple(parse):
    if isinstance(parse, compiler.ast.Name):
        return parse.name
    elif isinstance(parse, compiler.ast.CallFunc):
        return tuple([parseToTuple(x) for x in [parse.node] + parse.args])
    elif isinstance(parse, compiler.ast.List):
        return [parseToTuple(x) for x in parse.nodes]
    elif isinstance(parse, compiler.ast.And):
        return tuple(['and'] + [parseToTuple(x) for x in parse.nodes])
    elif isinstance(parse, compiler.ast.Or):
        return tuple(['or'] + [parseToTuple(x) for x in parse.nodes])
    elif isinstance(parse, compiler.ast.Const):   # a string constant used
        return "_" + parse.value
    else:
        print "Unhandled node type:", parse
        raise


def readPrimitive(line):
    # 'primitive a, b, c' means that a, b and c and primitive actions with their own names as the defining functions
    dash.primitiveActions(line[10:].split(", "))

def readProject(lines):
    print "Reading project rule from", lines
    goal = readGoalTuple(lines[0][lines[0].find(" "):].strip())
    effects = []
    # To handle multi-line preconditions, group lines into a longLine that
    # contains a " + " or " - "
    longLine = ""
    for line in lines[1:]:
        longLine += line
        if " + " in line or " - " in line:
            if "->" in longLine:
                [precondLine, effectLine] = longLine.split("->")
                effects.append(Effect(Effect.add if " + " in line else Effect.delete,
                                      readGoalTuple(effectLine[3:]),  # should find +/-
                                      readGoalTuple(precondLine),
                                      1))   # Not reading probability yet
            else:
                effects.append(Effect(Effect.add if " + " in line else Effect.delete,
                                      readGoalTuple(longLine[3:]), True, 1))
            longLine = ""
    # Store a list of projection rules indexed by the goal
    if goal not in projectionRuleDict:
        projectionRuleDict[goal] = []
    projectionRuleDict[goal].append(effects)

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

# Adds 'goal' as a known fact or completed goal
def knownTuple(t):
    if t[0] not in knownDict:
        knownDict[t[0]] = []
    if t not in knownDict[t[0]]:
        if traceKnown: print "recording as known", t
        knownDict[t[0]].append(t)

def known(predicate, arguments):
    knownTuple(tuple([predicate]) + tuple(arguments))  # this allows arguments to be any iterable

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
        elif dash.isPrimitive(subbed):
            if traceGoals: print ' '*indent, "returning primitive", subbed
            return subbed
        elif isGoal(subbed):
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
    print "unifying ", pattern, "and", candidate
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
    print "returns", bindings
    return bindings

def isConstant(term):
    # Anything other than a string is assumed to be a constant
    # This test assumes python 2.x
    return not isinstance(term, basestring) or term.startswith("_")

# Substitute bindings in tuple representation of a term,
# where the first argument is the predicate.
# Needs to support structure in the term arguments.
def substitute(predicate, bindings):
    if isinstance(predicate, (list, tuple)):
        args = [substituteArgument(arg,bindings) for arg in predicate[1:]]
        return tuple([predicate[0]] + args)
    return substituteArgument(predicate, bindings)

def substituteArgument(arg, bindings):
    if isinstance(arg, list):
        return [substituteArgument(x, bindings) for x in arg]
    elif isinstance(arg, tuple):
        return tuple([substituteArgument(x, bindings) for x in arg])
    elif arg not in bindings:
        return arg
    else:
        return bindings[arg]


#################
## Projection
#################

# A probabilistic effect should really be a list of alternatives whose
# probability sum to 1 but for now I'm just providing a probability p,
# and we assume that the alternative is nothing happening with prob 1-p.

class Effect(object):

    add = 1
    delete = 0
    
    def __init__(self, addOrDelete, term, precondition=True, probability=1):
        self.addOrDelete = addOrDelete  # 1 means add, 0 means delete
        self.term = term  # thing being added or deleted
        self.precondition = precondition
        self.probability = probability

def preferPlan(planA, planB):
    return expectedUtility(project(planA)) > expectedUtility(project(planB))

def project(plan, state=[]):
    worlds = [state]
    for step in plan:
        newWorlds = []
        for world in worlds:
            newWorlds = newWorlds + projectStep(step, world)
        worlds = newWorlds
    return worlds

# Project a single step by finding the appropriate projection rule
def projectStep(step, world):
    return [world]

def expectedUtility(worlds):
    return 0
