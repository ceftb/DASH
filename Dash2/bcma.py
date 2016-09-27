from dash import DASHAgent


class BCMAAgent(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.readAgent("""

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

# The second clause for the same goal is tried after the first one
# fails.
goalRequirements doFirstStepIfPreferred(plan)
  succeeds(plan)

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
  + _loggedIn

project document(meds, patient)
  performed(eMAR_Review(patient)) and performed(scan(patient))
  and performed(scan(meds)) and _loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  _nurseModel and performed(scan(patient)) and performed(scan(meds))
  and _loggedIn -> + performed(document(meds, patient))

project document(meds, patient)
  _nurseModel and _loggedIn -> 0.95 + performed(document(meds, patient))

project document(meds, patient)

# Still experimenting with this. This version is additive, e.g. each match to the given pattern
# in the final world increases the utility by the shown amount (decreases if negative)
utility
  performed(document(meds, patient)) -> 1

""")
        self.primitiveActions([['notKnown', self.notKnown],
                  ['buildPlan', self.buildPlan],
                  ['preferFirstStep', self.preferFirstStep],
                  ['remainder', self.remainder],
                  ['eMAR_Review', self.succeed],
                  ['retrieveMeds', self.succeed],
                  ['scan', self.succeed],
                  ['deliver', self.succeed],
                  ['ensureLoggedIn', self.succeed],
                  ['document', self.succeed],
                  ['succeeds', self.succeed],
                  ['doNothing', self.succeed]])

    # assume patient is bound and plan is not. Return bindings
    # for the plan
    def buildPlan(self, action):
        print "calling build plan with", action
        (patient, meds, plan) = action[1:]
        # instantiates the plan for the patient and meds
        return [{plan: [('eMAR_Review', patient),
        ('retrieveMeds', meds, patient),
        ('scan', patient),
        ('scan', meds),
        ('deliver', meds, patient),
        'ensureLoggedIn',
        ('document', meds, patient)]}]

    # If the first step in the plan is indicated, bind the step variable to it
    def preferFirstStep(self, action):
        (plan, stepVar) = action[1:]
        if self.preferPlan(plan, plan[1:]):
            return [{stepVar: plan[0]}]
        else:
            return False #[{stepVar: 'doNothing'}]

    # Binds the 'remainder' var to the remainder of the plan in the first var
    def remainder(self, action):
        (plan, remvar) = action[1:]
        if len(plan) < 1:
            return []
        else:
            return [{remvar: plan[1:]}]


if __name__ == "__main__":
    BCMAAgent().agentLoop(max_iterations=200)
