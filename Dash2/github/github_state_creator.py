import sys; sys.path.extend(['../../'])
from Dash2.socsim.network_utils import GraphBuilder, create_initial_state_files, IdDictionaryInMemoryStream
from Dash2.socsim.event_types import github_events, github_events_list


class GithubGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from Reddit events
    """

    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time, raw_json_event=None):
        GraphBuilder.update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time)
        # update node attributes: actionSubType and status
        #self.graph.edges[user_id, resource_id]["actionSubType"] = raw_json_event["actionSubType"]

    def finalize_graph(self):
        graph, number_of_users, number_of_resources = GraphBuilder.finalize_graph(self)
        # do something Github-specific here

        return graph, number_of_users, number_of_resources


if __name__ == "__main__":
    filename = "../socsim/data_sample.json" #sys.argv[1]
    create_initial_state_files(filename, GithubGraphBuilder, github_events, github_events_list,
                               dictionary_stream_cls=IdDictionaryInMemoryStream,
                               initial_state_generators=None)
