import random
import numbers


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


class Boolean(Parameter):

    def __init__(self, name, distribution=None, default=None):
        Parameter.__init__(self, name, distribution, default)

        # If the distribution is not filled if, default to equal chance True and False
        if distribution is None:
            self.distribution = Equiprobable([True, False])


# General class of distributions for parameters
class Distribution:

    def __init__(self):
        parameter = None  # A pointer to the parameter if useful, e.g. to get the value set
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


# This class currently assumes an immutable set of possible values, so the mean is precomputed if applicable.
class Equiprobable(Distribution):

    def __init__(self, values):
        self.values = values
        # Check this at build time so it is just done once
        self.numeric = all(isinstance(x, numbers.Number) for x in self.values)
        # May as well pre-compute the mean too
        self.mean = sum(self.values)/float(len(self.values)) if self.numeric else None

    def __repr__(self):
        return "Equiprobable(" + str(self.values) + ")"

    def sample(self):
        return random.choice(self.values)

    # mean is defined if all the values are numbers. Don't want to test that every time
    def mean(self):
        return self.mean

