from dash import DASHAgent, isVar


class SecurityUser(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
  decideEachStep([backUp(), engageFirewall(), followLink()])

goalRequirements decideEachStep([])

goalRequirements decideEachStep(plan)
  decideFirstStep(plan)
  remainder(plan, rest)
  decideEachStep(rest)

goalRequirements decideFirstStep(plan)
  preferFirstStep(plan, step)
  step

goalRequirements decideFirstStep(plan)
  succeed(_doNothing)

# Really for these two clauses we have model and not performed(action) -> unsafe in different ways
# But not sure I can match negatives yet
project followLink()
  _burglar_model and performed(engageFirewall()) -> + _safe
  _vandal_model and performed(backUp()) -> + _safe

utility
  _safe -> 1

""")
        self.known('_vandal_model')  # Assert the model(s) that the agent is using

    # Binds the 'remainder' var to the remainder of the plan in the first var
    def remainder(self, (predicate, plan, remainder_var)):
        if len(plan) < 1:
            return []
        else:
            return [{remainder_var: plan[1:]}]

    def back_up(self, goal):
        print 'back up with', goal
        self.known('_backedUp')
        return [{}]

    def follow_link(self, goal):
        print 'followed link with', goal
        self.known('_followedLink')
        return [{}]


if __name__ == "__main__":
    s = SecurityUser()
    s.agentLoop(max_iterations=200)
