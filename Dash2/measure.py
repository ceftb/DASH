
# A measure is a function of the agent state, possibly over a period of time or of a set of agents,
# that is used as a measure of the agent system performance.
# A measure can be associated either with an agent definition or an experiment, and can be added dynamically.
# There is an associated function to compute the measure.

# 'target' and 'backing' are currently in flux but are meant to represent a target value and experimental backing
# for the target value respectively. They should probably be grouped in an object so we can have multiple values
# and backings with conditions on them, e.g. the forgetting rate is X for teens, Y for elders in Singapore per paper P


class Measure:

    def __init__(self, name, function=None, target=None, backing=None):
        self.name = name
        self.function = function
        self.target = target
        self.backing = backing

