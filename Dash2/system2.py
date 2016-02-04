# Contains code relating to goal decomposition and mental model projection
import dash  # don't import specific names so this module will be compiled first
import compiler # Testing using the compiler to parse expressions
import time


goalWeightDict = dict()
goalRequirementsDict = dict()
knownDict = dict()
knownFalseDict = dict()
transientDict = dict()
projectionRuleDict = dict()
utilityRules = []


# Read the agent definition in a simpler syntax and create the appropriate definitions
traceLoad = False
traceParse = False


def readAgent(string):
    # state is used for multi-line statements like goalRequirements
    # and projection rules
    state = 0
    goalRequirements = 1
    project = 2
    utility = 3
    lines = []
    for line in string.split('\n'):
        if "#" in line:
            line = line[0:line.find("#")]
        line = line.strip()
        if state in [goalRequirements, project, utility]:
            if line == "":
                if state == goalRequirements:
                    readGoalRequirements(lines)
                elif state == project:
                    readProject(lines)
                elif state == utility:
                    readUtility(lines)
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
        elif line.startswith("utility"):
            state = utility
            lines = [line]
        elif line.startswith("transient"):
            readTransient(line)


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
    elif isinstance(parse, compiler.ast.Const):   # a string or other constant used
        if isinstance(parse.value, basestring):
            return "_" + parse.value
        else:
            return parse.value
    else:
        print "Unhandled node type:", parse
        raise BaseException


def readPrimitive(line):
    # 'primitive a, b, c' means that a, b and c and primitive actions with their own names as the defining functions
    dash.primitiveActions(line[10:].split(", "))


def readProject(lines):
    if traceParse:
        print "Reading projection rule from", lines
    goal = readGoalTuple(lines[0][lines[0].find(" "):].strip())
    effects = []
    # To handle multi-line preconditions, group lines into a longLine that
    # contains a " + " or " - "
    longLine = ""
    for line in lines[1:]:
        longLine += line
        effectLine = longLine
        condition = True
        if "+ " in line or "- " in line:
            if "->" in longLine:
                [precondLine, effectLine] = longLine.split("->")
                condition = readGoalTuple(precondLine)
            effects.append(readEffectLine(effectLine, condition))
            longLine = ""
    # Store a list of projection rules indexed by the goal
    head = goal
    if isinstance(goal, (list, tuple)):
        head = goal[0]
    if head not in projectionRuleDict:
        projectionRuleDict[head] = []
    projectionRuleDict[head].append((goal, effects))


def readEffectLine(line, condition=True):
    p = compiler.parse(line.strip()).node.nodes[0].expr
    if traceParse:
        print 'Parse for effect line', line, 'is', p
    # With no probabilities the results are UnaryAdd or UnaryDel, otherwise Add and Del,
    # Note the condition isn't included here
    if isinstance(p, compiler.ast.UnaryAdd):
        return Effect(Effect.add, parseToTuple(p.expr), condition, 1)
    elif isinstance(p, compiler.ast.UnarySub):
        return Effect(Effect.delete, parseToTuple(p.expr), condition, 1)
    elif isinstance(p, compiler.ast.Add):
        return Effect(Effect.add, parseToTuple(p.right), condition, p.left.value)
    elif isinstance(p, compiler.ast.Sub):
        return Effect(Effect.delete, parseToTuple(p.right), condition, p.left.value)
    else:
        print "No effects found", line
        return None


# Lines are of the form condition -> incr, and each match to condition increments
# utility by that amount.
def readUtility(lines):
    for line in lines[1:]:
        print "reading utility from", line
        [precond, incr] = line.split("->")
        utilityRules.append([readGoalTuple(precond.strip()), float(incr)])
    print "Utility rules are", utilityRules


def readTransient(line):
    goal = readGoalTuple(line[line.find(" "):].strip())
    predicate = goal
    if isinstance(goal, (list,tuple)):
        predicate = goal[0]
    if predicate not in transientDict:
        transientDict[predicate] = []
    transientDict[predicate].append(goal)
    print "Transient:", transientDict


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
    addTuple(t, knownDict)


def knownFalseTuple(t):
    addTuple(t, knownFalseDict)


def addTuple(t, adict):
    if t[0] not in adict:
        adict[t[0]] = []
    if t not in adict[t[0]]:
        if traceKnown: print "recording as known", t
        adict[t[0]].append(t)


def known(predicate, arguments):
    knownTuple(tuple([predicate]) + tuple(arguments))  # this allows arguments to be any iterable


def knownFalse(predicate, arguments):
    knownFalseTuple(tuple([predicate]) + tuple(arguments))


# Might be subgoal or top-level goal
def isGoal(goal):
    return goal[0] in goalRequirementsDict


def chooseAction():
    goal = chooseGoal()
    if goal is not None:
        return chooseActionForGoals([goal])
    else:
        return None


def chooseGoal():
    if goalWeightDict == {}:
        return None
    # Return a goal with highest weight that is not already achieved (always returns the same one)
    validGoals = [item for item in goalWeightDict.items() if isKnown(item[0]) is False]
    if validGoals:
        return max(validGoals, key=lambda pair: pair[1])[0]
    else:
        return None


# indent is used to print trace information with increasing indentation
traceGoals = False


def chooseActionForGoals(goals, indent=0):
    if goals is None:
        return None
    if traceGoals: print ' '*indent, "Seeking action for goals", goals
    gpb = findGoalRequirements(goals[0])
    if gpb is []:
        print "No goal requirements match for ", goals[0]
        return None
    if traceGoals: print ' '*indent, "Requirements:", gpb
    i = 1
    for (goal, requirements, bindings) in gpb:
        if traceGoals: print ' '*indent, ' ', 'trying req set', i, goal, requirements, bindings
        # Return the first unfulfilled action in the requirements body, substituting bindings
        # but try the next requirements (if any) if there is a knownFalse subgoal in the requirements
        na = nextAction(goal, requirements, bindings, indent)
        if na is not False and na is not None:
            return na
        i += 1
    return None


# Recursively move through subgoals and return the next primitive action
# To add: return False if a subgoal is knownFalse
def nextAction(goal, requirements, bindings, indent):
    for candidate in requirements[1]:
        subbed = substitute(candidate, bindings)
        if traceGoals:
            print ' '*indent, "inspecting requirement", subbed, "from", candidate
        newBindings = isKnown(subbed)
        if newBindings is not False:
            if traceGoals:
                print ' '*indent, candidate, "known with bindings", newBindings
            bindings = dict(bindings.items() + newBindings.items())  # wasteful but succinct
            continue
        elif isKnownFalse(subbed) is not False:  # a part of this goalset has been tried and failed in the past
            return None
        elif dash.isPrimitive(subbed):
            if traceGoals:
                print ' '*indent, "returning primitive", subbed
            return subbed
        elif isGoal(subbed):
            action = chooseActionForGoals([subbed], indent + 2)
            if action is not None and action[0] == 'known':
                # This subgoal was achievable from what is already done.
                # Update bindings
                if traceGoals:
                    print ' '*indent, candidate, "already achieved"
                bindings = dict(bindings.items() + action[1].items())
                continue
            else:
                return action
        else:
            print ' '*indent, subbed, "is not a goal or primitive or already known"
            return None
    # If we got here, then we went through all the subactions without needing to do anything,
    # So the goal should be marked as achieved
    subbedGoal = substitute(goal,bindings)
    if not isTransient(subbedGoal):
        knownTuple(subbedGoal)
        if traceGoals:
            print "Marking", subbedGoal, "as achieved"
    return ['known', bindings]   # This return value lets the function know when subgoals are achieved vacuously
    

# Known kind of conflates other ways of knowing things with knowing that a
# subgoal has been performed
def isKnown(goal):
    return isIn(goal, knownDict)


def isKnownFalse(goal):
    return isIn(goal, knownFalseDict)

def isTransient(goal):
    print "checking transient", goal, transientDict
    return isIn(goal, transientDict)


# Create a list of all the known facts, used for projection
# (Simple def used for functional abstraction)
def knownList():
    return [fact for goal in knownDict for fact in knownDict[goal]]


def isIn(goal, adict):
    if goal[0] in adict:
        for term in adict[goal[0]]:
            bindings = unify(goal, term)
            if bindings != False:  # Since {} means success with no new bindings
                return bindings
    return False


def findGoalRequirements(goal):
    if goal[0] in goalRequirementsDict:
        # Return all possible bindings since we may be backtracking on them.
        # Later want to use an incrementally-build structure rather than a list.
        result = []
        for pair in goalRequirementsDict[goal[0]]:
            bindings = unify(goal, pair[0])
            if bindings != False:
                result.append((goal, pair, bindings))
        return result
    else:
        return []


# Return bindings that would unify the pattern with the candidate, or False
traceUnify = False
def unify(pattern, candidate, bindings=None):
    if bindings is None: bindings = {}   # Cannot create dict in the argslist, or it's shared between every call
    if traceUnify:
        print "Trying unify", pattern, candidate, bindings
        
    if isVar(pattern):
        if traceUnify:
            print "Pattern is variable:", pattern
        if pattern == candidate:
            return bindings
        elif pattern in bindings and isConstant(bindings[pattern]):  # treat this as if it were the constant its bound to. Don't bind vars to vars to avoid loops
            return unify(bindings[pattern], candidate, bindings)
        elif not isVar(candidate):
            if pattern in bindings: # bound to another variable. Bind them both to this constant
                bindings[bindings[pattern]] = candidate
            bindings[pattern] = candidate
            return bindings
        elif candidate in bindings:
            bindings[pattern] = bindings[candidate]
            return bindings
        else:
            bindings[pattern] = candidate
            return bindings
    elif isVar(candidate):   # candidate is a variable but pattern is not
        if traceUnify:
            print "Candidate", candidate, "is variable, not pattern", pattern
        return unify(candidate, pattern, bindings)  # Use the case above
    elif isinstance(pattern, (list, tuple)):  # recursively match structures
        # Assume the first argument is a predicate name which has to be equal
        if isinstance(candidate, (list, tuple)) and len(pattern) == len(candidate) and pattern[0] == candidate[0]:
            if traceUnify:
                print "Pattern", pattern, "is a tuple, recursing"
            # Match the arguments in the goal and the requirements head
            for (goalarg, matcharg) in zip(pattern[1:], candidate[1:]):
                bindings = unify(goalarg, matcharg, bindings)
                if bindings is False:
                    return False
            return bindings
        else:
            if traceUnify:
                print "Pattern is a tuple but candidate is not, or has different predicate or length:", pattern, candidate
            return False
    elif candidate != pattern: # constants must match
        if traceUnify:
            print "Non-matching constants"
        return False
    elif candidate == pattern:
        if traceUnify:
            print "Same objects"
        return bindings


# Just clarifies the code a little
def isConstant(term):
    return not isVar(term)


def isVar(term):
    # Anything other than a string is assumed to be a constant
    # This test assumes python 2.x
    return isinstance(term, basestring) and not term.startswith("_")


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

    def __repr__(self):
        return "<effect: %s -> %s %s>" % (self.precondition, '+' if self.addOrDelete == self.add else '-', self.term)

    # return a world after this effect happens in the input world (list of facts)
    def do(self, world, bindings):
        if isinstance(self.term, (list, tuple)):
            fact = substitute(self.term, bindings)
        else:
            fact = self.term
        if self.addOrDelete == Effect.add:
            if fact not in world:
                world.append(fact)   # surgically alters the list
        elif fact in world:
            world.remove(fact)
        return world


def preferPlan(planA, planB, initialWorld=None):
    if initialWorld == None:  # by default, start from what's known in the world
        initialWorld=knownList()
    expA = expectedUtility(project(planA, initialWorld))
    expB = expectedUtility(project(planB, initialWorld))
    return expA > expB


def project(plan, state=[]):
    worlds = [state]
    for step in plan:
        newWorlds = []
        for world in worlds:
            newWorlds = newWorlds + projectStep(step, world)
        worlds = newWorlds
    print "Projecting", plan, "\n  yields", worlds
    return worlds


# Project a single step by finding the appropriate projection rule
def projectStep(step, world):
    #print 'projecting', step, 'on', world
    head = step   # predicate for the rule, which is the step if it's a string..
    if isinstance(step, (list, tuple)):
        head = step[0]  #.. and otherwise the first element
    if head in projectionRuleDict:
        rules = projectionRuleDict[head]
        for rule in rules:
            bindings = unify(rule[0], step) if isinstance(step, (list, tuple)) else True
            if bindings != False:
                #print "Rule", rule, "matches with bindings", bindings
                for effect in rule[1]:
                    if effect.precondition == True or matchPrecond(substitute(effect.precondition, bindings), world):
                        world = effect.do(world, bindings)
                return [world]
    # Default effect if no rule matched
    return [world + [('performed', step)]]


def matchPrecond(precond, world):
    #print "Matching", precond
    if precond == True:
        return True
    if isinstance(precond, (tuple, list)) and precond[0] == 'and':
        for subPrecond in precond[1:]:
            if not matchPrecond(subPrecond, world):
                return False
        return True
    elif isinstance(precond, (tuple, list)) and precond[0] == 'or':
        for subPrecond in precond[1:]:
            if matchPrecond(subPrecond, world):
                return True
        return False
    elif isinstance(precond, (tuple, basestring)):    # match a single goal
        return precond in world                       # trying to avoid python2-specific match
    else:
        return False


def expectedUtility(worlds):
    # Assume each world has the same weight and return the average utility
    return sum([utility(world) for world in worlds])/float(len(worlds))


def utility(world):
    total = 0
    for rule in utilityRules:
        total += len(allMatches(rule[0], world)) * rule[1]
    return total


# Return a list of bindings list for all the ways a pattern can be matched
# in a world (list of facts). Not doing any fancy matching, so it's exponential.
# currentBindings defaults to one, empty, bindings list.
def allMatches(pattern, world, allBindings=[{}]):
    # Filter the world for the printout
    # Punting on 'and' and 'or' for now
    # For a term, extend each bindings list in every possible way
    if isinstance(pattern, (tuple, list)):
        matches =  [b for b in [unify(fact, pattern, bindings) for fact in world for bindings in allBindings]
                    if b is not False]
        return matches
    return []


traceForget = False


# This is a primitive built-in to remove all items matching a pattern from
# knownDict and knowFalseDict
def forget(action):
    print "Forgetting", action[1]
    for pattern in action[1]:
        if not isinstance(pattern, (tuple, list)):
            continue
        predicate = pattern[0]
        for d in [knownDict, knownFalseDict]:
            if predicate in d:
                # not sure if I can modify the list I'm iterating across
                toRemove = []
                for fact in d[predicate]:
                    if unify(pattern, fact) is not False:
                        if traceForget:
                            print "Forgetting", fact
                        toRemove.append(fact)
                for fact in toRemove:
                    d[predicate].remove(fact)
    return [{}]  # succeed as a primitive action, with no bindings

transientDict['forget']=[('forget', 'x')]  # Forget should be transient so you can keep forgetting things

def sleep(action):
    print "Sleeping", action[1]
    time.sleep(action[1])
    return [{}]

# Tests
#print unify(('p', ('p', 'b')), ('p', ('p', '_x')))

