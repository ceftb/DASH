import random


class Parameter:

    def __init__(self, name, distribution=None, default=None):
        self.name = name
        self.distribution = distribution
        self.default = default

    def __repr__(self):
        string = "P[" + self.name + ", " + str(self.distribution)
        if self.default is not None:
            string += ", " + str(self.default)
        return string + "]"


# General class of distributions for parameters
class Distribution:

    def __init__(self):
        pass

    def __repr__(self):
        return "Null distribution"

    # Returns a value randomly drawn from the distribution
    def sample(self):
        pass

    def mean(self):
        pass


class Uniform(Distribution):

    def __init__(self, min, max):
        self.min_value = min
        self.max_value = max

    def __repr__(self):
        return "Uniform(" + str(self.min_value) + ", " + str(self.max_value) + ")"

    def sample(self):
        return random.uniform(self.min_value, self.max_value)

    def mean(self):
        return (self.max_value - self.min_value)/2.0

