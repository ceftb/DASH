import sys; sys.path.extend(['../../'])
import networkx as nx
from Dash2.socsim.network_utils import GraphBuilder, build_graph_from_json
import json
import os.path
import time
import numpy as np
import cPickle as pickle
import ijson
from Dash2.socsim.distributed_event_log_utils import load_id_dictionary, collect_unique_user_event_pairs
from Dash2.socsim.event_types import domains, reddit_events, reddit_events_list


class RedditGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from reddit events
    """
    def __init__(self):
        pass #GraphBuilder.__init__(self)

    def update_graph(self, event):
        self.event_counter += 1



def create_initial_state_files(input_json, initial_state_generators=None):
    #build_graph_from_json(input_json, RedditGraphBuilder())
    pass



