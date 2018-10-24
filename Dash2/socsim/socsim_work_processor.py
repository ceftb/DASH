import sys; sys.path.extend(['../../'])
import os.path
import os
import psutil
import time
import cPickle as pickle
import json
from heapq import heappush, heappop
from Dash2.core.work_processor import WorkProcessor

# Work processor performs simulation as individual process (it is a DashWorker)
class SocsimWorkProcessor(WorkProcessor):

    # this is path to current package. Trial class needs it
    module_name = "Dash2.socsim.socsim_work_processor"

    def initialize(self):
        self.agents_decision_data = {}
        self.events_heap = []
        self.event_counter = 0
        self.task_start_time = time.time()

        # hub object
        hub_mod = __import__(self.hub_module_name, fromlist=[self.hub_class_name])
        hub_cls = getattr(hub_mod, self.hub_class_name)
        self.hub = hub_cls(self.zk, self.task_full_id, 0, self.output_file_name) #self.hub = RedditHub(self.zk, self.task_full_id, 0, self.output_file_name)

        # agent object
        mod = __import__(self.agent_module_name, fromlist=[self.agent_class_name])
        cls = getattr(mod, self.agent_class_name)
        self.agent =cls(useInternalHub=True, hub=self.hub, skipS12=True, trace_client=False, traceLoop=False, trace_github=False)

        # network
        self.hub.graph = pickle.load(open(self.UR_graph_path, "rb"))

        # id dictionaries
        initial_state_meta_data = json.load(open(self.initial_state_file))["meta"]
        self.hub.users_ids = pickle.load(open(initial_state_meta_data["users_ids"]))
        self.hub.resource_ids = pickle.load(open(initial_state_meta_data["resource_ids"]))

        for node_id in self.hub.graph:
            if self.hub.graph.nodes[node_id]["isU"] == 1:
                decision_data = self.agent.create_new_decision_object(node_id)
                self.agent.decision_data = decision_data
                first_event_time = self.agent.first_event_time(self.start_time)
                if first_event_time is not None:
                    heappush(self.events_heap, (self.agent.next_event_time(self.start_time), decision_data.id))
                self.agents_decision_data[decision_data.id] = decision_data # node_id == decision_data

        self.hub.agents_decision_data = self.agents_decision_data # will not work for distributed version
        self.hub.finalize_statistics()
        self.hub.mamory_usage = self._get_current_memory_usage()
        print "Agents instantiated: ", len(self.agents_decision_data)

    def run_one_iteration(self):
        event_time, agent_id = heappop(self.events_heap)
        decision_data = self.agents_decision_data[int(agent_id)]
        self.hub.set_curr_time(event_time)
        self.agent.decision_data = decision_data
        self.agent.agentLoop(max_iterations=1, disconnect_at_end=False)
        next_event_time = self.agent.next_event_time(event_time)
        if next_event_time < self.max_time:
            heappush(self.events_heap, (next_event_time, agent_id))
        self.event_counter += 1

    def should_stop(self):
        if self.max_iterations > 0 and self.iteration >= self.max_iterations:
            print 'reached end of iterations for trial'
            self.hub.memory_usage = self._get_current_memory_usage()
            return True
        if len(self.events_heap) == 0:
            print 'reached end of event queue, no more events'
            self.hub.memory_usage = self._get_current_memory_usage()
            return True
        return False

    def _get_current_memory_usage(self):
        pid = os.getpid()
        py = psutil.Process(pid)
        memory_use = float(py.memory_info()[0]) / (1024.0 * 1024.0 * 1024.0) # in GB
        return memory_use

    def get_dependent_vars(self):
        return {"num_agents": len(self.agents_decision_data),
                "num_resources": -1,
                #"total_agent_activity": sum([a.total_activity for a in self.agents_decision_data.viewvalues()]),
                "number_of_cross_process_communications": self.hub.sync_event_counter,
                "memory_usage": self.hub.memory_usage,
                "runtime": time.time() - self.task_start_time
                }

    def process_after_run(self):  # do any book-keeping needed after the trial ends and before agents are disconnected
        self.hub.close_event_log()
        self.log_file.close()
        os.remove(self.task_full_id + '_event_log_file.txt')

