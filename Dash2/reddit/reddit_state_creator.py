import sys; sys.path.extend(['../../'])
import json
import os.path
import time
import numpy as np
import cPickle as pickle
import ijson
from Dash2.socsim.distributed_event_log_utils import load_id_dictionary, collect_unique_user_event_pairs
from Dash2.socsim.event_types import domains, reddit_events, reddit_events_list


def create_initial_state_files(input_json, initial_state_generators=None):
    pass


