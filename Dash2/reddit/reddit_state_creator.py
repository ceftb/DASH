import sys; sys.path.extend(['../../'])
from Dash2.socsim.network_utils import GraphBuilder, create_initial_state_files, IdDictionaryInMemoryStream
from Dash2.socsim.event_types import reddit_events, reddit_events_list


class RedditGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from Reddit events
    """

    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time, raw_json_event=None):
        GraphBuilder.update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time)
        # update node attributes: communityID": "t5_3bqj4"
        if "cmt" not in self.graph.nodes[user_id]:
            self.graph.nodes[user_id]["cmt"] = {}
        self.graph.nodes[user_id]["cmt"][raw_json_event["communityID"]] = self.graph.nodes[user_id]["cmt"][raw_json_event["communityID"]] + 1.0 \
            if raw_json_event["communityID"] in self.graph.nodes[user_id]["cmt"] else 0.0

    def finalize_graph(self):
        graph, number_of_users, number_of_resources = GraphBuilder.finalize_graph(self)
        # do something Reddit-specific here

        return graph, number_of_users, number_of_resources


if __name__ == "__main__":
    filename = "../socsim/data_sample.json" #sys.argv[1]
    create_initial_state_files(filename, RedditGraphBuilder, reddit_events, reddit_events_list,
                               dictionary_stream_cls=IdDictionaryInMemoryStream,
                               initial_state_generators=None)
