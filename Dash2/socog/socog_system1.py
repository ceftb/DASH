from socog_module import BeliefModule
from socog_module import ConceptPair


class SocogSystem1Agent(object):
    """

    """

    tokens = {
        'and' : self._and,
        'or' : self._or,
        'not' : self._not,
        '(' : '(',
        ')' : ')',
        'True' : True,
        'False' : False
    }

    def __init__(self, belief_module=None):
        """

        :param belief_module:
        """

        if belief_module is None:
            self._belief_module = BeliefModule()
        else:
            self._belief_module = belief_module

        # A list of tuples. The first element is the condition, the second a
        # sequence of actions.
        self.rule_list = []
        self.belief_token_map = {}

    def _and(self, a, b):
        """
        evaluates: a and b
        :param a: a boolean
        :param b: a boolean
        :return: boolean
        """

        return a and b

    def _or(self, a, b):
        """
        evaluates: a or b
        :param a: a boolean
        :param b: a boolean
        :return: boolean
        """

        return a or b

    def _not(self, a):
        """
        evaluates: not a
        :param a: a boolean
        :return: boolean
        """
        return not a

    def read_system_rules(self, rule_string):
        """
        Adds rules from the given string into the list of rules in the socog
        system.

        :param rule_string: A string containing lines for each system rule.
            A system rule is defined by a condition and sequence of actions.
            If the condition is fulfilled, the sequence is carried out. The
            condition is a logical statement that can use and, or, not, and
            parentheses. The action statement is a sequence of primitive actions
            separated by spaces. The conditions must specify beliefs, which
            require three values to be specified: two concepts and a valence.
            E.g:
                if [A,B,0.5] and [C,B,-0.2] then run(speed) jump(height)

            Square brackets are used to designate a belief. Each concept and
            the valence are separated by ','.

            Note: setting valence to 0.0 is ambiguous and will return True if
                the agent has the belief.
            Note: The 'True' word can be used to designate conditions that will
                always return true, e.g.:
                    if True then talk(belief) call(belief)

        :return: None
        """
        # Parse string into sub-strings for each rule
        for rule in rule_string.splitlines():
            self.rule_list.append(self._split_rule_into_action_and_condition(rule))

        self.belief_token_map.update(self._construct_belief_token_map(self.rule_list))

    def _is_belief_token(self, token):

        if ((token != ')') and (token != '(') and (token != 'and') and
                (token != 'not') and (token != 'True') and (token != 'False')):
            return True

        return False

    def _construct_belief_token_map(self, rule_list):
        """
        Creates concept_pair, valence tuple from belief tokens
        :param rule_list: a tokenized list of rules
        :return: dictionary keyed by belief token and valued by a tuple:
            (concept_pair, valence)
        """

        belief_token_map = {}
        for rule in rule_list:
            for token in rule:
                if self._is_belief_token(token):
                    split_token = token.split(",")
                    belief_token_map[token] = (ConceptPair(
                        split_token[0], split_token[1]), float(split_token[2]))

        return belief_token_map

    def _split_condition_string_into_tokens(self, condition_string):
        """
        Splits the condition string into a list of tokens, e.g. terminals
        and operators and parentheses.
        :param condition_string: a string representation of the condition
        :return: token list
        """

        condition_string = condition_string.replace(" ", "")\
            .replace('(', ' ( ')\
            .replace(')', ' ) ')\
            .replace('andnot', ' and not ')\
            .replace('[', ' [')\
            .replace(']', '] ')\
            .replace('[', '')\
            .replace(']', '')

        return condition_string.split(" ")

    def _split_rule_into_action_and_condition(self, rule):
        """
        Splits a single rule, represented as a string, into a condition string
        and an action string.
        :param rule: a single if/then string
        :return: tuple (condition string, action string)
        """

        # Strip everything unnecessary for condition and action parsing
        condition, action = rule.split("then")
        condition = condition.strip()
        condition = condition.replace("if", "", 1)
        action = action.strip().split(" ")

        return self._split_condition_string_into_tokens(condition), action

    # def _check_condition(self, condition):
    #     """
    #     Parses the condition strings and evaluates whether they are satisfied
    #     or not.
    #     :param condition: a condition string
    #     :param pos: position of pointer
    #     :return: boolean
    #     """
    #
    #     current_element =
    #
    #     if

    def _is_belief_token_satisfied(self, belief_token):
        """
        :param belief_token: string representing a belief
        :return: True/False
        """

        return self._is_belief_condition_satisfied(*self.belief_token_map[belief_token])

    def _is_belief_condition_satisfied(self, concept_pair, valence):
        """
        Checks if the condition is satisfied in the belief system
        :param concept_pair
        :param valence
        :return: boolean
        """

        if concept_pair in self._belief_module.belief_network:
            if (abs(valence)
                    >= abs(self._belief_module.belief_network.beliefs[concept_pair])):
                return True

        return False

    def listen(self, action):

        pass

    def talk(self, action):

        pass

    def spreading_activation(self):

        pass

    def system1_decay(self):

        pass

    def actions_over_threshold(self, threshold):
        """

        :param threshold:
        :return: A list of iterable things that have a node_to_action method
        """

        return #list of

    def add_activation(self, fact, activation_increment=0.3):

        pass


# Something needs this....................
def node_to_action(self):

    pass

    return # an action?