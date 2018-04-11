from Dash2.socog.socog_module import BeliefModule
from Dash2.socog.socog_module import ConceptPair
from collections import deque


class SocogSystem1Agent(object):
    """
    A system1-like class that uses a belief module and system rules to fill
    a queue of actions that the agent will attempt to take
    """

    boolean_token = {'and', 'or', 'not', 'true', 'false'}

    def __init__(self, belief_module=None):
        """
        :param belief_module: A BeliefModule object
        """

        if belief_module is None:
            self.belief_module = BeliefModule()
        else:
            self.belief_module = belief_module

        # A list of tuples. The first element is the condition, the second a
        # sequence of actions.
        self.rule_list = []
        self.belief_token_map = {}
        self.action_queue = deque()

    def read_system1_rules(self, rule_string):
        """
        Adds rules from the given string into the list of rules in the socog
        system1.

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
                self.add_token_to_map(token, belief_token_map)

        return belief_token_map

    def add_token_to_map(self, token, token_map):
        """
        Checks if token is valid, and if so, adds it to the map in-place
        :param token: a condition token
        :return: same reference to map
        """
        if System1Evaluator.is_belief_token(token):
            split_token = token.split(",")
            concept_pair = ConceptPair(split_token[0], split_token[1])
            token_map[token] = (concept_pair, float(split_token[2]))
            # To keep variable order invariant have to swap variables
            doppelganger_token = self._swap_token_variables(split_token)
            token_map[doppelganger_token] = (concept_pair,
                                             float(split_token[2]))

        return token_map

    @staticmethod
    def parse_string_to_tokens(condition_string):
        """
        Splits the condition string into a list of tokens, e.g. terminals
        and operators and parentheses and actions.
        :param condition_string: a string representation of the condition
        :return: token list
        """
        slice_start = Index(0)
        slice_end = Index(1)
        tokens = []
        while slice_start.pos < len(condition_string):
            if condition_string[slice_start.pos].isalnum() \
                    or condition_string[slice_start.pos] == '[':
                tokens.append(SocogSystem1Agent.parse_token_expression(
                    condition_string, slice_start, slice_end))
                slice_start.pos = slice_end.pos

            elif condition_string[slice_start.pos] == ')':
                tokens.append(')')

            elif condition_string[slice_start.pos] == '(':
                tokens.append('(')

            elif condition_string[slice_start.pos] == ']':
                raise ValueError("Error: unexpected closing bracket ]")

            slice_start.increment()
            slice_end.pos = slice_start.pos + 1

        return tokens

    @staticmethod
    def parse_token_expression(condition_string, slice_start, slice_end):

        if condition_string[slice_start.pos] == '[':
            slice_start.increment()
            while condition_string[slice_end.pos] != ']':
                slice_end.increment()

        elif condition_string[slice_start.pos].isalnum():
            while slice_end.pos < len(condition_string):

                if (condition_string[slice_start.pos:slice_end.pos].lower()
                    in SocogSystem1Agent.boolean_token) \
                       and condition_string[slice_end.pos] == ' ':
                    break

                if condition_string[slice_end.pos] == '(':
                    while condition_string[slice_end.pos] != ')':
                        slice_end.increment()
                    slice_end.increment()
                    break

                slice_end.increment()

        return condition_string[slice_start.pos:slice_end.pos].replace(' ','')

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

        return SocogSystem1Agent.parse_string_to_tokens(condition), action

    def is_belief_condition_satisfied(self, concept_pair, valence):
        """
        Checks if the condition is satisfied in the belief system
        :param concept_pair
        :param valence
        :return: boolean
        """

        if concept_pair in self.belief_module.belief_network:
            if (abs(valence)
                    >= abs(self.belief_module.belief_network.beliefs[concept_pair])):
                return True

        return False

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

    def reset_action_queue(self, action_list):
        """
        Empties queue, and calculates what conditions are satisfied and adds
        them to the queue.
        :return: None
        """
        self.action_queue.clear()
        self.action_queue.extend(action_list)

    def add_actions_to_queue(self, action_list):
        """
        Adds actions to the right of the action queue
        :param action_list: a list of primitive actions
        :return: None
        """
        self.action_queue.extend(action_list)


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


class System1Evaluator(object):
    """
    Helper class that evaluates system1agent rules
    """

    def __init__(self, socog_agent):
        """
        :param socog_agent: A SocogDASHAgent
        """
        self.socog_agent = socog_agent
        self._recursion_flag = False

    boolean_non_operands = {'and', 'or', 'not', '(', ')'}
    binary_operators = {'and', 'or'}

    @staticmethod
    def is_operand_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return token.lower() not in System1Evaluator.boolean_non_operands

    @staticmethod
    def is_binary_operator_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return token.lower() in System1Evaluator.binary_operators

    @staticmethod
    def is_belief_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return token.count(',') == 3

    @staticmethod
    def is_action_token(token):
        """
        :param token: a tokenized string
        :return: boolean
        """

        return ('(' in token) and (')' in token)

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

        return System1Evaluator.is_binary_operator_token(tokens[index.pos])

    def _is_belief_token_satisfied(self, belief_token):
        """
        :param belief_token: string representing a belief
        :return: True/False
        """

        if belief_token in self.socog_agent.belief_token_map:
            return self.socog_agent.is_belief_condition_satisfied(
                *self.socog_agent.belief_token_map[belief_token])

        elif System1Evaluator.is_belief_token(belief_token):
            self.socog_agent.add_token_to_map(belief_token,
                                              self.socog_agent.belief_token_map)
            return self._is_belief_token_satisfied(belief_token)

        else:
            raise ValueError("Error: Invalid token input <" +
                             belief_token + "> does not have a truth value")

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

            while System1Evaluator.valid_operator_token(tokens, index):
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

        if System1Evaluator.is_belief_token(tokens[index.pos]):
            token_evaluation = self._is_belief_token_satisfied(tokens[index.pos])
            index.increment()
            return token_evaluation

        if System1Evaluator.is_action_token(tokens[index.pos]):
            # Recursion flag is to prevent actions from
            # resetting the stack and condition check indefinitely
            self._recursion_flag = True
            token_evaluation = self.evaluate_action(tokens[index.pos])
            self._recursion_flag = False
            index.increment()
            return token_evaluation is True

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

    def is_condition_satisfied(self, condition):
        """
        Parses the condition tokens and evaluates whether they are satisfied
        or not.
        :param condition: a tokenized list from the rule_list
        :return: boolean
        """

        return self.parse_expression(condition)

    def actions_from_satisfied_conditions(self):
        """
        Check all conditions in rule_list and return a list of actions
        that satisfy those conditions
        :return: A list of iterable things that have a node_to_action method
        """

        active_actions = []
        for condition, actions in self.socog_agent.rule_list:
            if self.is_condition_satisfied(condition):
                active_actions += actions

        return active_actions

    def evaluate_action(self, action):

        result = self.socog_agent.performAction(action)
        self.socog_agent.update_beliefs(result, action)
        return result

    def initialize_action_queue(self):
        """
        Fills system1's action queue with actions found to satisfy the
        conditions of its rules.

        Uses a recursion flag to prevent actions that are called from the
        condition check to call another condition check.

        :return: None
        """
        if not self._recursion_flag:
            self.socog_agent.reset_action_queue(self.actions_from_satisfied_conditions())
