import sys; sys.path.extend(['../../'])
from Dash2.socsim.socsim_hub import SocsimHub
from Dash2.socsim.output_event_log_utils import random_pick_sorted
import datetime


# Zookeeper hub for socsim agents
class RedditHub(SocsimHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    sync_event_counter = 0

    def __init__(self, zk, task_full_id, start_time, output_file_name):
        SocsimHub.__init__(self, zk, task_full_id, start_time, output_file_name)

    # this overrides default log method in SocsimHub
    def log_event(self, user_id, resource_id, event_type, time, additional_attributes=None):
        #self.print_to_csv_log(user_id, resource_id, event_type, self._convert_time(time), additional_attributes)
        # add id convertion
        self.print_to_json_log(user_id, resource_id, event_type, int(time), additional_attributes)