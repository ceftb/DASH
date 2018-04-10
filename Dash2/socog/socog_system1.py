from Dash2.socog.socog_module import BeliefModule
from Dash2.socog.socog_module import ConceptPair
from Dash2.core.system1 import Node
from collections import deque


class Index(object):
    """
    Implements a wrapper around an integer to allow a mutable int-like interface
    """
    def __init__(self, pos=0):
        self.pos = pos

    def increment(self):
        self.pos += 1

    def decrement(self):
        self.pos -= 1


class SocogSystem1Agent(object):
    """
    A system1-like class that uses a belief module and system rules to fill
    a queue of actions that the agent will attempt to take
    """
    def __init__(self, belief_module=None):
        """
        :param belief_module: A BeliefModule object
        """

        if belief_module is None:
            self._belief_module = BeliefModule()
        else:
            self._belief_module = belief_module

        # A list of tuples. The first element is the condition, the second a
        # sequence of actions.
        self.rule_list = []
        self.belief_token_map = {}
        self.action_queue = deque()

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
                    if [True] then talk(belief) call(belief)
                    if [false] or not [TRUE] then talk(belief) call(belief)

            Note: precedence is from left to right or determined by parenthesis

        :return: None
        """
        # Parse string into sub-strings for each rule
        for rule in rule_string.splitlines():
            self.rule_list.append(self._split_rule_into_action_and_condition(rule))

        self.belief_token_map.update(self._construct_belief_token_map(self.rule_list))

    def _swap_token_variables(self, split_belief_token):
        """
        Swaps variable location and builds a new string with concept locations
        swapped.
        :param split_belief_token: a belief token that has been split into its
            elements
        :return: a string representing the same token but with variable locations
            swapped.
        """

        return split_belief_token[1] + "," + split_belief_token[0] \
               + "," + split_belief_token[2]

    def _construct_belief_token_map(self, rule_list):
        """
        Creates concept_pair, valence tuple from belief tokens
        :param rule_list: a tokenized list of rules
        :return: dictionary keyed by belief token and valued by a tuple:
            (concept_pair, valence)
        """

        belief_token_map = {}
        for rule in rule_list:
            for token in rule[0]:
                self._add_token_to_map(token, belief_token_map)

        return belief_token_map

    def _add_token_to_map(self, token, token_map):
        """
        Checks if token is valid, and if so, adds it to the map in-place
        :param token: a condition token
        :return: same reference to map
        """
        if SocogSystem1Agent.is_belief_token(token):
            split_token = token.split(",")
            concept_pair = ConceptPair(split_token[0], split_token[1])
            token_map[token] = (concept_pair, float(split_token[2]))
            # To keep variable order invariant have to swap variables
            doppelganger_token = self._swap_token_variables(split_token)
            token_map[doppelganger_token] = (concept_pair,
                                             float(split_token[2]))

        return token_map

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
            .replace('ornot', ' or not ')\
            .replace('[', ' [')\
            .replace(']', '] ')\
            .replace('[', '')\
            .replace(']', '')

        return condition_string.split()

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

    def _is_belief_token_satisfied(self, belief_token):
        """
        :param belief_token: string representing a belief
        :return: True/False
        """

        if belief_token in self.belief_token_map:
            return self._is_belief_condition_satisfied(
                *self.belief_token_map[belief_token])

        elif belief_token == 'True':
            return True

        elif belief_token == 'False':
            return False

        elif SocogSystem1Agent.is_belief_token(belief_token):
            self._add_token_to_map(belief_token, self.belief_token_map)
            return self._is_belief_token_satisfied(belief_token)

        else:
            raise ValueError("Error: Invalid token input <" +
                             belief_token + "> does not have a truth value")

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

    boolean_non_operands = {'and', 'or', 'not', '(', ')'}

    binary_operators = {'and', 'or'}

    @staticmethod
    def is_operand_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return token.lower() not in SocogSystem1Agent.boolean_non_operands

    @staticmethod
    def is_binary_operator_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return token.lower() in SocogSystem1Agent.binary_operators

    @staticmethod
    def is_belief_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return SocogSystem1Agent.is_operand_token(token) \
            and (token.lower() != 'true') \
            and (token.lower() != 'false')

    @staticmethod
    def valid_operator_token(tokens, index):
        """
        Returns True if the token at index.pos exists and is an operator
        :param tokens: a list of tokens
        :param index: Index object
        :return: boolean
        """

        if index.pos >= len(tokens):
            return False

        return SocogSystem1Agent.is_binary_operator_token(tokens[index.pos])

    def parse_expression(self, tokens, index=None):
        """
        A boolean logic parser that is implemented as a recursive decent parser.
        :param tokens: list of tokens
        :param index: index location in tokens (default 0)
        :return: boolean value
        """

        if index is None:
            index = Index()

        while index.pos < len(tokens):
            is_negated = False
            if tokens[index.pos].lower() == 'not':
                is_negated = True
                index.increment()

            evaluation = self.parse_subexpression(tokens, index)
            if is_negated:
                evaluation = not evaluation

            while SocogSystem1Agent.valid_operator_token(tokens, index):
                operator = tokens[index.pos].lower()
                index.increment()
                if index.pos >= len(tokens):
                    raise IndexError("Error: Missing expression after operator: "
                                     + str(tokens[index.pos - 1]) + " at "
                                     + str(index.pos))

                next_evaluation = self.parse_subexpression(tokens, index)
                if operator == 'and':
                    evaluation = evaluation and next_evaluation
                elif operator == 'or':
                    evaluation = evaluation or next_evaluation
                else:
                    raise AssertionError("Error: Unknown operator")

            return evaluation

        raise IndexError("Empty expression")

    def parse_subexpression(self, tokens, index=None):
        """
        Parses subexpressions. Is a part of the parse_expression function.
        :param tokens: list of tokens
        :param index: index location in tokens (default 0)
        :return: boolean value
        """
        if index is None:
            index = Index()

        if SocogSystem1Agent.is_belief_token(tokens[index.pos]):
            token_evaluation = self._is_belief_token_satisfied(tokens[index.pos])
            index.increment()
            return token_evaluation

        elif tokens[index.pos].lower() == 'true':
            index.increment()
            return True

        elif tokens[index.pos].lower() == 'false':
            index.increment()
            return False

        elif tokens[index.pos] == '(':
            index.increment()
            expression_eval = self.parse_expression(tokens, index)
            if tokens[index.pos] != ')':
                raise IndexError("Error: Expected closed parenthesis")

            index.increment()
            return expression_eval

        elif tokens[index.pos] == ')':
            raise IndexError("Error: Unexpected closed parenthesis")

        else:
            return self.parse_expression(tokens, index)

    def _is_condition_satisfied(self, condition):
        """
        Parses the condition tokens and evaluates whether they are satisfied
        or not.
        :param condition: a tokenized list from the rule_list
        :return: boolean
        """

        return self.parse_expression(condition)

    def listen(self, args):
        """
        Takes a two element tuple. The second element must be a Beliefs object
        which system1 will use to update the belief module. Once updated,
        the action queue will be emptied and the rules will be checked for
        satisfied conditions. The action queue will be re-filled with new
        active actions from the rule list.
        :param args: goal, belief tuple
        :return: Empty [{}]
        """
        goal, belief = args
        self._belief_module.listen(belief)
        self.reset_action_queue()
        return [{}]

    def talk(self, args):
        """
        Calls the belief module's talk method to get and return a Beliefs
        object with the agents chosen belief for emission.
        :param args: goal, belief tuple
        :return: single element list with dictionary. key=belief, value=Beliefs
        """
        goal, belief = args
        return [{belief: self._belief_module.talk()}]

    def select_action_from_queue(self):
        """
        :return: Selects an action at the front of the queue. If no actions
            remain, it returns None. Pops actions from the front (left) of the
            queue.
        """

        try:
            return self.action_queue.popleft()
        except IndexError:
            return None

    def actions_from_satisfied_conditions(self):
        """
        Check all conditions in rule_list and return a list of actions
        that satisfy those conditions
        :return: A list of iterable things that have a node_to_action method
        """

        active_actions = []
        for condition, actions in self.rule_list:
            if self._is_condition_satisfied(condition):
                active_actions += actions

        return active_actions

    def reset_action_queue(self):
        """
        Empties queue, and calculates what conditions are satisfied and adds
        them to the queue.
        :return: None
        """
        self.action_queue.clear()
        self.action_queue.extend(self.actions_from_satisfied_conditions())

    def add_actions_to_queue(self, action_list):
        """
        Adds actions to the right of the action queue
        :param action_list: a list of primitive actions
        :return: None
        """
        self.action_queue.extend(action_list)
