from dash import readAgent, isKnown, primitiveActions, agentLoop, goalRequirements, goalWeight, preferPlan

readAgent("""

goalWeight doWork 1

goalRequirements doWork
  deliverMeds(!joe, !percocent)
  deliverMeds(!brian, !codeine)

goalRequirements deliverMeds(patient, medication)
  notKnown(document(patient,medication))
  buildPlan(patient, medication, plan)
  preferFirstStep(plan)
  decidePerformRest(plan)

goalRequirements decidePerformRest([])

goalRequirements decidePerformRest(plan)
  remainder(plan, rest)
  preferFirstStep(rest)
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
  .

project ensureLoggedIn
  + loggedIn

project document(meds, patient)
  performed(eMAR_Review(patient)) and performed(scan(patient))
  and performed(scan(meds)) and loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  nurseModel and performed(scan(patient))
  and performed(scan(meds)) and loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  nurseModel and loggedIn -> 0.95 + performed(document(meds, patient))

project document(meds, patient)
  .

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
    (patient, plan) = action[1:]
    patient = patient[1:]
    # instantiates the plan for the patient and meds
    return [{plan: [('eMAR_Review', patient),
                    ('retrieveMeds', patient, meds),
                    ('scan', patient),
                    ('scan', meds),
                    ('deliver', meds, patient),
                    'ensureLoggedIn',
                    ('document', meds, patient)]}]

def preferFirstStep(plan):
    if preferPlan(plan, plan[1:]):
        return [{}]
    else:
        return []

# Binds the 'remainder' var to the remainder of the plan in the first var
def remainder(action):
    (plan, remvar) = action[1:]
    remvar = remvar[1:]
    if len(plan) < 1:
        return []
    else:
        return [{remvar: plan[1:]}]
