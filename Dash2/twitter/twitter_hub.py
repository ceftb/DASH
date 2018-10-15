import sys; sys.path.extend(['../../'])
from Dash2.socsim.socsim_hub import SocsimHub
from Dash2.socsim.output_event_log_utils import random_pick_sorted
import datetime


# Zookeeper hub for socsim agents
class TwitterHub(SocsimHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    sync_event_counter = 0

    def __init__(self, zk, task_full_id, start_time, log_file):
        SocsimHub.__init__(self, zk, task_full_id, start_time, log_file)
