import random
import numbers


class Parameter:

    def __init__(self, name, distribution=None, default=None, value_set=None, range=None):
        self.name = name
        self.distribution = distribution
        self.default = default
        self.value_set = value_set  # value_set may be a list or a range such as Range(0,1) (assumed to be closed)
        if value_set is None and range is not None:
            self.value_set = Range(range[0], range[1])

    def __repr__(self):
        string = "P[" + self.name + ", " + \
                 (str(self.distribution) if self.distribution is not None else str(self.value_set))
        if self.default is not None:
            string += ", " + str(self.default)
        return string + "]"


class Boolean(Parameter):

    def __init__(self, name, distribution=None, default=None):
        Parameter.__init__(self, name, distribution, default, value_set=[True, False])

        # If the distribution is not filled if, default to equal chance True and False
        if distribution is None:
            self.distribution = Equiprobable(self.value_set)


# A continuous closed range of numbers
class Range:

    def __init__(self, min_val, max_val):
        self.min = min_val
        self.max = max_val

    def __repr__(self):
        return "Range(" + str(self.min) + ", " + str(self.max) + ")"


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

    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def __repr__(self):
        return "Uniform(" + str(self.min_value) + ", " + str(self.max_value) + ")"

    def sample(self):
        return random.uniform(self.min_value, self.max_value)

    def mean(self):
        return (self.max_value - self.min_value)/2.0


# This class currently assumes an immutable finite set of possible values, so the mean is precomputed if applicable.
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

