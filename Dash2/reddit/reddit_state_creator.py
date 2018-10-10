import sys; sys.path.extend(['../../'])
from Dash2.socsim.network_utils import GraphBuilder, create_initial_state_files
from Dash2.socsim.event_types import reddit_events, reddit_events_list


class RedditGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from reddit events
    """

    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time):
        if not self.graph.has_node(resource_id):
            self.graph.add_node(resource_id, pop=0, isU=0)

        event_index = reddit_events[event_type]
        if self.graph.has_node(user_id):
            self.graph.nodes[user_id]["r"] += 1.0
        else:
            self.graph.add_node(user_id, shared=0, isU=1)
            self.graph.nodes[user_id]["r"] = 1.0
            self.graph.nodes[user_id]["ef"] = [0] * len(reddit_events_list)
            self.graph.nodes[user_id]["ef"][event_index] += 1
            self.graph.nodes[user_id]["pop"] = 0  # init popularity
            # event-resource pair frequencies:
            self.graph.nodes[user_id]["e_r"] = {}
        self.graph.nodes[user_id]["let"] = event_time

        if self.graph.has_edge(resource_id, user_id):
            self.graph.add_edge(resource_id, user_id, weight=self.graph.get_edge_data(resource_id, user_id)['weight'] + 1)
        else:
            self.graph.add_edge(resource_id, user_id, own=0, weight=1)
            self.graph.get_edge_data(resource_id, user_id)['ef'] = [0] * len(reddit_events_list)
        self.graph.get_edge_data(resource_id, user_id)['ef'][event_index] += 1
        # event-resource pair frequencies:
        event_repo_pair = (event_index, resource_id)
        if event_repo_pair not in self.graph.nodes[user_id]["e_r"]:
            self.graph.nodes[user_id]["e_r"][event_repo_pair] = 0.0

        self.graph.nodes[user_id]["e_r"][event_repo_pair] += 1.0

        # popularity of resources
        if event_type == "reply":
            self.graph.nodes[resource_id]["pop"] += 1



if __name__ == "__main__":
    filename = "../socsim/data_sample.json" #sys.argv[1]
    create_initial_state_files(filename, RedditGraphBuilder)
