import sys; sys.path.extend(['../../'])
from Dash2.socsim.socsim_hub import SocsimHub
from Dash2.socsim.distributed_event_log_utils import random_pick_sorted
import datetime


# Zookeeper hub for socsim agents
class TwitterHub(SocsimHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    sync_event_counter = 0

    def __init__(self, zk, task_full_id, start_time, log_file):
        SocsimHub.__init__(self, zk, task_full_id, start_time, log_file)

    def finalize_statistics(self):
        if self.userIdAndPopularity is not None:
            random_pick_sorted(self.userIdAndPopularity["ids"], self.userIdAndPopularity["probability"])
        for var_data in self.aggregated_statistic.itervalues():
            aggregation_function = var_data["func"]
            if aggregation_function is not None:
                aggregation_function(var_data, self.aggregated_statistic, isFinalUpdate=True)

            # global event clock
    def set_curr_time(self, curr_time):
        self.time = curr_time

    def log_event(self, user_id, repo_id, event_type, subevent_type, time):
        date = datetime.datetime.fromtimestamp(time)
        str_time = date.strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(str_time)
        self.log_file.write(",")
        self.log_file.write(event_type)
        self.log_file.write(",")
        self.log_file.write(str(user_id))
        self.log_file.write(",")
        self.log_file.write(str(repo_id))
        #self.log_file.write(subevent_type)
        #self.log_file.write(",")
        self.log_file.write("\n")

    def processRegisterRequest(self, agent_id, aux_data):
        creation_time = self.time
        return ["success", aux_data["id"], creation_time]
