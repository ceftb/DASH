from dash import readAgent, isKnown, primitiveActions, agentLoop, goalRequirements, goalWeight, preferPlan

import system2

readAgent("""

goalWeight doWork 1

goalRequirements doWork
  deliverMeds(_joe, _percocet)
  deliverMeds(_brian, _codeine)

goalRequirements deliverMeds(patient, medication)
  notKnown(document(patient, medication))
  buildPlan(patient, medication, plan)
  doFirstStepIfPreferred(plan)
  decidePerformRest(plan)

# These are probably general subgoals that should be available to all agents
goalRequirements doFirstStepIfPreferred(plan)
  preferFirstStep(plan, step)  # returns false or binds the step to perform
  step

goalRequirements doFirstStepIfPreferred(plan)

goalRequirements decidePerformRest(plan)
  remainder(plan, rest)
  doFirstStepIfPreferred(rest)
  decidePerformRest(rest)

# For envisioning a plan, relative to a mental model
# If there's no rule for an action under certain conditions, 
#  the 'performed' predicate is added for the action but nothing else
# To delete a fact, put a minus sign '-' in front of the fact.
# The model is a precondition like any other fact, but is not added or deleted.

project deliver(meds, patient)
  performed(retrieveMeds(meds, patient)) -> + performed(deliver(meds, patient))

# This turns off the default of adding 'performed(..)'
project deliver(meds, patient)

project ensureLoggedIn
  + loggedIn

project document(meds, patient)
  performed(eMAR_Review(patient)) and performed(scan(patient))
  and performed(scan(meds)) and loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  nurseModel and performed(scan(patient)) and performed(scan(meds)) 
  and loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  nurseModel and loggedIn -> 0.95 + performed(document(meds, patient))

project document(meds, patient)

""")

                 
# utility primitive - probably should be in system2
# Need 'not' in there properly as well as deep variable replacement
def notKnown(predicate):
    print "calling notknown with", predicate
    if isKnown(predicate):
        return []
    else:
        return [{}]

# assume patient is bound and plan is not. Return bindings
# for the plan
def buildPlan(action):
    print "calling build plan with", action
    (patient, meds, plan) = action[1:]
    # instantiates the plan for the patient and meds
    return [{plan: [('eMAR_Review', patient),
                    ('retrieveMeds', patient, meds),
                    ('scan', patient),
                    ('scan', meds),
                    ('deliver', meds, patient),
                    'ensureLoggedIn',
                    ('document', meds, patient)]}]

# If the first step in the plan is indicated, bind the step variable to it
def preferFirstStep(action):
    (plan, stepVar) = action[1:]
    if preferPlan(plan, plan[1:]):
        return [{stepVar: plan[0]}]
    else:
        return []

# Binds the 'remainder' var to the remainder of the plan in the first var
def remainder(action):
    (plan, remvar) = action[1:]
    if len(plan) < 1:
        return []
    else:
        return [{remvar: plan[1:]}]

# This action should perhaps be part of the main code. It just
# succeeds, and right now prints out that the action was called.
def succeed(action):
    print "Primitive action", action, "trivially succeeds"
    return [{}]

primitiveActions([['notKnown', notKnown],
                  ['buildPlan', buildPlan],
                  ['preferFirstStep', preferFirstStep],
                  ['remainder', remainder],
                  ['eMAR_Review', succeed],
                  ['retrieveMeds', succeed],
                  ['scan', succeed],
                  ['deliver', succeed],
                  ['ensureLoggedIn', succeed],
                  ['document', succeed]])

agentLoop(maxIterations=12)
