import sys; sys.path.extend(['../../'])
from Dash2.socsim.network_utils import GraphBuilder, create_initial_state_files
from Dash2.socsim.event_types import twitter_events, twitter_events_list


class TwitterGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from Twitter events
    """

    def finalize_graph(self):
        # finalize
        return GraphBuilder.finalize_graph(self)


    def update_nodes_and_edges(self, user_id, resource_id, event_type, event_time, raw_json_event=None):
        GraphBuilder.update_nodes_and_edges(self, user_id, resource_id, event_type, event_time)
        root_resource_id = self.resource_id_dict.update_dictionary(raw_json_event["rootID"])
        parent_resource_id = self.resource_id_dict.update_dictionary(raw_json_event["parentID"])

        # roots
        if "rts" not in self.graph.nodes[user_id]:
            self.graph.nodes[user_id]["rts"] = {}
        else:
            if root_resource_id not in self.graph.nodes[user_id]["rts"]:
                self.graph.nodes[user_id]["rts"][root_resource_id] = 0
            else:
                self.graph.nodes[user_id]["rts"][root_resource_id] += 1
        # parents
        if "prns" not in self.graph.nodes[user_id]:
            self.graph.nodes[user_id]["prns"] = {}
        else:
            if parent_resource_id not in self.graph.nodes[user_id]["prns"]:
                self.graph.nodes[user_id]["prns"][parent_resource_id] = 0
            else:
                self.graph.nodes[user_id]["prns"][parent_resource_id] += 1



if __name__ == "__main__":
    filename = "../socsim/data_sample.json" #sys.argv[1]
    create_initial_state_files(filename, TwitterGraphBuilder, twitter_events, twitter_events_list)

