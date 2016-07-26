# Contains code managing instinctive behavior and spreading activation

# In the first iteration, system 1 has a set of nodes, which have facts and activation strengths.
# Facts take the same form as predicates in system 2 and allow unification with activation rules.
# Each node is updated and may update its neighbors once per iteration. Nodes with high enough
# activation may affect system2 reasoning, or override it if the node chooses an action to
# perform.


class Node:
    node_id = -1
    activation = 0
    fact = None
    neighbors = []
    change_since_update = 0

    def __init__(self, node_id, fact, activation=0, neighbors=[]):
        self.node_id = node_id
        self.fact = fact
        self.activation = activation
        self.neighbors = neighbors

    def __str__(self):
        return "N" + str(self.node_id) + ": " + str(self.fact) + ", " + str(self.activation)\
               + "nx: " + str([n.node_id for n in self.neighbors])

    def __repr__(self):
        return self.__str__()

    def update(self, activation_increment):
        self.change_since_update += activation_increment

    def spread(self):
        if self.change_since_update != 0:
            for neighbor in self.neighbors:
                neighbor.update(self.change_since_update/3)
            self.change_since_update = 0


class System1Agent:
    nodes = set()
    fact_node_dict = dict()

    trace_add_activation = False

    def __init__(self):
        self.system1Fact = set()

    # Main DASH agent communicates activation for a fact. This looks up the node with fact_node_dict, adding
    # if necessary, and increments the activation
    def add_activation(self, fact, activation_increment=0.3):
        n = self.fact_to_node(fact)
        if self.trace_add_activation:
            print 'adding activation to', n
        n.update(activation_increment)

    def spreading_activation(self):
        for node in self.nodes:
            node.spread()

    def nodes_over_threshold(self, threshold=0.5):
        return [n for n in self.nodes if n.activation >= threshold]

    # Turn a fact into a unique key by removing spaces and writing brackets into a string
    # so ('hi', ('there', 'you')) becomes "[hi[there,you]]"
    def fact_to_key(self, fact):
        if isinstance(fact, (list,tuple)):
            result = "["
            for sub_fact in fact:
                result += ("," if len(result) > 1 else "") + self.fact_to_key(sub_fact)
            return result + "]"
        else:
            return str(fact)

    # Given a fact, return its node, creating a new one if needed.
    def fact_to_node(self, fact):
        key = self.fact_to_key(fact)
        if key not in self.fact_node_dict:
            self.fact_node_dict[key] = Node(len(self.nodes) + 1, fact)
            self.nodes.add(self.fact_node_dict[key])
        return self.fact_node_dict[key]

    # Create a spreading activation rule, that sets up neighbors for nodes that match the rule
    # and reinforcement strengths.
    def create_spread_rule(self, node_pattern, action):
        pass
