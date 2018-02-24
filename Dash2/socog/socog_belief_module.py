from collections import namedtuple
from collections import deque
from copy import copy
from random import Random
from math import exp

# An immutable object representing a concept w/ name and id
Concept = namedtuple('Concept', ['name', 'id'])


class ConceptPair(tuple):
    """
    An immutable object representing a pair of concepts
    Elements can be independently accessed but is still hashable and 
    order doesn't matter: 
    E.g. ConceptPair(concept1,concept2) == ConceptPair(concept2,concept1)
    """
    __slots__ = []
    def __new__(cls, concept1, concept2):
        return tuple.__new__(cls, (concept1, concept2))

    @property
    def concept1(self):
        return tuple.__getitem__(self, 0)

    @property
    def concept2(self):
        return tuple.__getitem__(self, 1)

    def __getitem__(self, item):
        raise TypeError

    def __eq__(self, other):
        """
        A belief is equivalent to another if both of its concepts are the
        same. Even though it is a tuple underneath, there is no element order
        """

        return ((tuple.__getitem__(self, 0) == other.concept1) and 
                (tuple.__getitem__(self, 1) == other.concept2)) or \
               ((tuple.__getitem__(self, 0) == other.concept2) and 
                (tuple.__getitem__(self, 1) == other.concept1))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset(self))


class ConceptTriad(tuple):
    """
    An immutable object that represents a triangle, of three concepts. 
    Internally it is represented as 3 ConceptPairs.
    Elements can be independently accessed but are 
    still hashable and order doesn't matter: 
    E.g. ConceptTriad(concept1,concept2,concept3) == ConceptTriad(concept2,concept3,concept1)
    """
    __slots__ = []
    def __new__(cls, concept1, concept2, concept3):
        return tuple.__new__(cls, (ConceptPair(concept1, concept2), 
                                   ConceptPair(concept2, concept3), 
                                   ConceptPair(concept3, concept1)))

    @property
    def pair1(self):
        return tuple.__getitem__(self, 0)

    @property
    def pair2(self):
        return tuple.__getitem__(self, 1)

    @property
    def pair3(self):
        return tuple.__getitem__(self, 2)

    def __getitem__(self, item):
        raise TypeError

    def __eq__(self, other):
        """
        A belief is equivalent to another if both of its concepts are the
        same. Even though it is a tuple underneath, there is no element order
        """

        return ((tuple.__getitem__(self, 0) in other) and
                (tuple.__getitem__(self, 1) in other) and
                (tuple.__getitem__(self, 2) in other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset(self))


class Beliefs(dict):
    """
    An object that represents a set of beliefs
    """

    def __init__(self, *args):
        """
        Can be initialized with a dictionary keyed by ConceptPairs and valued
        by valences
        """
        dict.__init__(self, *args)

    def add_belief(self, concept_pair, valence):
        dict.__setitem__(self, concept_pair, valence)

    def __mul__(self, other):
        """
        This implements the dot product between two sets of beliefs.
        The operation is only carried out such that the overlapping subset of 
        beliefs that belong to both sets will contribute to the product.
        It only makes sense this way as non-overlapping elements would 
        multiply to 0 and not contribute to the sum.

        If a scalar is used, it multiplies the all valences by the scalar.
        """
        if isinstance(other, BeliefNetwork):
            dot_product = 0.0
            for other_pair, other_valence in other.beliefs.items():
                if other_pair in self:
                    dot_product += self.__getitem__(other_pair) * other_valence
            return dot_product

        elif isinstance(other, Beliefs):
            dot_product = 0.0
            for other_pair, other_valence in other.items():
                if other_pair in self:
                    dot_product += self.__getitem__(other_pair) * other_valence
            return dot_product

        else:
            # Scalar case
            for belief in self.keys():
                self[belief] *= other
            return self

    # Ensure commutivity of dot product
    __rmul__ = __mul__


class BeliefNetwork(object):
    """
    Nodes represent concepts in the belief network and edges represent a
    valenced relationship between those concepts. The valence can be positive or
    negative or a value between -1 and 1. No connection means no relationship.
    Triads of beliefs are checked for stability:
        +++ is stable
        -++ is unstable
        --+ is stable
        --- is unstable
    Edges can be weighted. The product of the weights specifies triad stability,
    with a positive value being stable and negative being unstable.

    A BeliefNetwork can be modified in-place via addition with another
    beliefnetwork or a belief through the += or -= operators. However,
    generaly support for +/- is not provided.

    The energy of the beliefnetwork is the internal energy, not to be confused
    with the social energy.
    """

    def __init__(self, beliefs=None):
        """
        beliefs - A Beliefs type
        """

        if beliefs is None:
            beliefs = Beliefs()

        self.beliefs = beliefs
        self.concept_set = self._find_all_concepts(self.beliefs.keys())
        self.triangle_set = self._find_all_triangles(self.beliefs.keys(), 
                                            self.beliefs, 
                                            self.concept_set)
        self.energy = self._calc_energy(self.triangle_set, self.beliefs)

    def __str__(self):

        return str(self.beliefs)

    def __iadd__(self, other):
        """
        In place addition. If adding a beliefnetwork or beliefs, then
        valences are added to the respective pairs. If a pair doesn't
        exist, then it is initialized to 0 and the addition continues. 
        If adding a scalar, then scalar is added to valences of all pairs.
        The energy is updated after the 
        """
        if isinstance(other, BeliefNetwork):
            for concept_pair, valence in other.beliefs.items():
                if concept_pair in self.beliefs:
                    self.beliefs[concept_pair] += valence
                else:
                    self.beliefs[concept_pair] = valence
                    self._update_containers(concept_pair)
                    
            self.update_energy()
            return self

        elif isinstance(other, Beliefs):
            for concept_pair, valence in other.items():
                if concept_pair in self.beliefs:
                    self.beliefs[concept_pair] += valence
                else:
                    self.beliefs[concept_pair] = valence
                    self._update_containers(concept_pair)
                    
            self.update_energy()
            return self

        else:
            # Scalar case
            for belief in self.beliefs.keys():
                self.beliefs[belief] += other

            self.update_energy()
            return self

    def __isub__(self, other):
        """
        In place substraction. If adding a beliefnetwork or beliefs, then
        valences are subtracted from the respective pairs. If a pair doesn't
        exist, then it is initialized to 0 and the subtraction continues. 
        If adding a scalar, then scalar is subtracted from valences of all pairs.
        """
        if isinstance(other, BeliefNetwork):
            for concept_pair, valence in other.beliefs.items():
                if concept_pair in self.beliefs:
                    self.beliefs[concept_pair] -= valence
                else:
                    self.beliefs[concept_pair] = -valence
                    self._update_containers(concept_pair)

            self.update_energy()
            return self

        elif isinstance(other, Beliefs):
            for concept_pair, valence in other.items():
                if concept_pair in self.beliefs:
                    self.beliefs[concept_pair] -= valence
                else:
                    self.beliefs[concept_pair] = -valence
                    self._update_containers(concept_pair)
                    
            self.update_energy()
            return self

        else:
            # Scalar case
            for belief in self.beliefs.keys():
                self.beliefs[belief] -= other

            self.update_energy()
            return self

    def __mul__(self, other):
        """
        This implements the dot product between two sets of beliefs.
        The operation is only carried out such that the overlapping subset of 
        beliefs that belong to both sets will contribute to the product.
        It only makes sense this way as non-overlapping elements would 
        multiply to 0 and not contribute to the sum.

        If a scalar is used, it multiplies the all valences by the scalar.
        """
        if isinstance(other, BeliefNetwork):
            dot_product = 0.0
            for other_pair, other_valence in other.beliefs.items():
                if other_pair in self.beliefs:
                    dot_product += self.beliefs[other_pair] * other_valence
            return dot_product

        elif isinstance(other, Beliefs):
            dot_product = 0.0
            for other_pair, other_valence in other.items():
                if other_pair in self.beliefs:
                    dot_product += self.beliefs[other_pair] * other_valence
            return dot_product

        else:
            # Scalar case
            for belief in self.beliefs.keys():
                self.beliefs[belief] *= other
            return self

    # Ensure commutivity of dot product
    __rmul__ = __mul__

    def _find_all_concepts(self, beliefs):
        """
        Generates a list of nodes in the network (also known as concepts)
        """
        return set([concept for concept_pair in beliefs
                    for concept in list(concept_pair)])

    def _find_all_triangles(self, beliefs, belief_set, concept_set):
        """
        Generates a set of triangles in the network
        """
        triangle_set = set()
        for concept_pair in beliefs:
            new_triangles = self._find_triangles_with_concept_pair(concept_pair,
                                triangle_set, belief_set, concept_set)
            triangle_set.update(new_triangles)

        return triangle_set

    def _find_triangles_with_concept_pair(self, concept_pair, triangle_set, 
        belief_set, concept_set):
        """
        finds triangles that have the concept pair as a link
        """
        new_triangles = set()
        for concept in concept_set:
            if ConceptPair(concept_pair.concept1, concept) in belief_set \
            and ConceptPair(concept_pair.concept2, concept) in belief_set:
                triangle = ConceptTriad(concept_pair.concept1, 
                                        concept_pair.concept2, concept)
                if triangle not in triangle_set:
                    new_triangles.add(triangle)

        return new_triangles

    def _calc_energy(self, triad_sequence, beliefs):

        energy = 0.0
        for triad in triad_sequence:
            energy += self._triad_energy_contribution(triad, beliefs)

        return energy

    def _triad_energy_contribution(self, triad, beliefs):

        return -beliefs[triad.pair1] \
                * beliefs[triad.pair2] \
                * beliefs[triad.pair3]

    def _add_concepts(self, concept_pair):

        if concept_pair.concept1 not in self.concept_set:
            self.concept_set.add(concept_pair.concept1)
        if concept_pair.concept2 not in self.concept_set:
            self.concept_set.add(concept_pair.concept2)

    def add_belief(self, belief):
        """
        add belief to the network and update the internal energy
        """

        concept_pair, valence = next(belief.iteritems())
        if concept_pair in self.beliefs:
            if self.beliefs[concept_pair] != valence:
                self.beliefs[concept_pair] = valence
                self.energy = self._calc_energy(self.triangle_set, self.beliefs)
        else:
            self.beliefs[concept_pair] = valence
            new_triangles = self._find_triangles_with_concept_pair(concept_pair,
                self.triangle_set, self.beliefs, self.concept_set)
            self._add_concepts(concept_pair)
            self.energy += self._calc_energy(new_triangles, self.beliefs)
            self.triangle_set.update(new_triangles)

    def _update_containers(self, concept_pair):
        """
        updates triangle_set, concepts, and beliefs
        """
        if concept_pair not in self.beliefs:
            self.beliefs[concept_pair] = 0

        self._add_concepts(concept_pair)
        self.triangle_set.update(self._find_triangles_with_concept_pair(
            concept_pair, self.triangle_set, self.beliefs, self.concept_set))

    def update_energy(self):
        """
        Recalculates the energy given the current state of the network
        """

        self.energy = self._calc_energy(self.triangle_set, self.beliefs)

    def __copy__(self):
        """
        Make a fast copy that by-passes the expensive __init__ function of
        the beliefnetwork. Uses an empty_copy function that carries out this
        __init__ by-pass
        """
        newcopy = empty_copy(self)
        newcopy.beliefs = copy(self.beliefs)
        newcopy.concept_set = copy(self.concept_set)
        newcopy.triangle_set = copy(self.triangle_set)
        newcopy.energy = self.energy
        return newcopy


def empty_copy(obj):
    """
    Subclass object and overwrite __init__ function to by-pass expensive
    initialization functions.
    """
    class Empty(obj.__class__):
        def __init__(self): pass
    newcopy = Empty()
    newcopy.__class__ = obj.__class__
    return newcopy


class BeliefModule(object):
    """
    Represents a cognitive module for assessing the coherence of an agents
    belief system. It handles receiving (listen) and sending (talk) beliefs,
    updating the belief network of the agent, and determining whether to 
    accept or reject new beliefs.
    """
    def __init__(self, **kwargs):
        """
        belief_net: a BeliefNetwork type object. default=BeliefNetwork()
        perceived_net: a BeliefNetwork type object representing the agent's
            perception of other's beliefs. default=BeliefNetwork()
        seed: seed number for rng. default=1
        max_memory: how many steps back the agent remembers incoming beliefs.
            This can be used in methods for outputing popular/recent beliefs.
            default=1
        T: Higher T will increase the likelihood of accepting beliefs that would
            increase the agents energy. default=1.0
        J: coherentism, controls contribution of internal belief system energy to
            total energy. default=1.0
        I: peer-influence, controls contribution of social energy to the total
            energy. default=1.0
        tau: float between [1,inf]. Higher values prefer older beliefs
            and reduce the contribution of newer beliefs to perceived beliefs.
            default=1.0
        recent_belief_chance: [0,1], the probability of choosing a belief to
            emit from short-term memory. If a recent belief isn't chosen, then
            a belief is chosen uniformly at random from the belief network.
            default=0.0
        """
        self.belief_network = kwargs.get("belief_net", BeliefNetwork())
        self.perceived_belief_network = kwargs.get("perceived_net", BeliefNetwork())
        self._max_memory = kwargs.get("max_memory", 1)
        self._memory = deque(maxlen=self._max_memory)
        self._seed = kwargs.get("seed", 1)
        self._rng = Random(self._seed)
        self.recent_belief_chance = kwargs.get("recent_belief_chance", 0.0)
        self.T = kwargs.get("T", 1.0)
        self.J = kwargs.get("J", 1.0)
        self.I = kwargs.get("I", 1.0)
        self.tau = kwargs.get("tau", 1.0)

    def seed(self, integer):
        """
        re-seeds rng
        """
        self._rng.seed(integer)
        self._seed = integer

    def _is_belief_acceptable(self, belief):
        """
        Given a belief will return True if acceptable else False.
        Creates a shallow copy of the belief network and adds the new belief
        to calculate the internal and social energy of a candidate belief.
        If the belief would lower the total energy it is accepted, else it
        is accepted with some probability.
        """

        current_social_energy = -(self.belief_network * self.perceived_belief_network)
        current_total_energy = self.J * self.belief_network.energy + self.I * current_social_energy

        candidate_belief_net = copy(self.belief_network)
        candidate_belief_net.add_belief(belief)
        candidate_social_energy = -(candidate_belief_net * self.perceived_belief_network)

        candidate_total_energy = self.J * candidate_belief_net.energy + self.I * candidate_social_energy

        if candidate_total_energy < current_total_energy:
            return True
        else:
            if (exp((current_total_energy - candidate_total_energy) / self.T) ) > self._rng.random():
                return True

        return False

    def _add_belief_to_memory(self, belief):
        """
        Adds an accepted belief to memory
        If memory would exceed its maximum capacity the oldest memory
        is dropped from the deque
        """

        if len(self._memory) < self._max_memory:
            self._memory.append(belief)
        else:
            self._memory.popleft()
            self._memory.append(belief)

    def _update_perceived_beliefs(self, belief):
        """
        See documentation for explanation of update equation
        """

        concept_pair, valence = next(belief.iteritems())
        current_valence = self.perceived_belief_network.beliefs[concept_pair]
        self.perceived_belief_network.beliefs[concept_pair] += 1. / self.tau * (
            valence - current_valence)

    def talk(self):
        """
        chooses and emits a belief from belief network from memory or from
        their belief network
        """

        if (self._rng.random() < self.recent_belief_chance) and (len(self._memory) != 0):
            return self._rng.choice(self._memory)
        else:
            return Beliefs((self._rng.choice(self.belief_network.beliefs.items()),))

    def listen(self, belief):
        """
        evaluates veracity of incoming belief
        if the agent likes and accepts it, it will also be added to their
        short term memory
        """

        self._update_perceived_beliefs(belief)

        if self._is_belief_acceptable(belief):
            self._add_belief_to_memory(belief)
            self.belief_network.add_belief(belief)
