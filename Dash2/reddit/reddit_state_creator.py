import sys; sys.path.extend(['../../'])
from Dash2.socsim.network_utils import GraphBuilder, create_initial_state_files, IdDictionaryInMemoryStream
from Dash2.socsim.event_types import reddit_events, reddit_events_list


class RedditGraphBuilder(GraphBuilder):
    """
    A class that creates user graph from Reddit events
    """

    def finalize_graph(self):
        # finalize
        return GraphBuilder.finalize_graph(self)

    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time, raw_json_event=None):
        GraphBuilder.update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time)


if __name__ == "__main__":
    filename = "../socsim/data_sample.json" #sys.argv[1]
    create_initial_state_files(filename, RedditGraphBuilder, reddit_events, reddit_events_list,
                               dictionary_stream_cls=IdDictionaryInMemoryStream,
                               initial_state_generators=None)
