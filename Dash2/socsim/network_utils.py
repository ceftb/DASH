import sys; sys.path.extend(['../../'])
import networkx as nx
import json
import os.path
import time
import numpy as np
import cPickle as pickle
import ijson
from datetime import datetime


class IdDictionaryStream:
    """
    A stream that creates user or resource dictionary files
    """
    def __init__(self, dictionary_filename, int_id_offset=0):
        self.entities = {}
        self.offset = int_id_offset
        self.file_stream = self._open(dictionary_filename)
        self._append_line("src_id", "sim_id")
        self.is_stream_open = True

    def update_dictionary(self, original_entity_id):
        if original_entity_id is not None and original_entity_id != "" and original_entity_id != "None":
            hash_entity_id = hash(original_entity_id)
            int_entity_id = self._conver_to_conseq_int_ids(hash_entity_id)

            if hash_entity_id not in self.entities:
                self.entities[hash_entity_id] = int_entity_id
                self._append_line(int_entity_id, original_entity_id)

            return int_entity_id
        else:
            return None

    def _conver_to_conseq_int_ids(self, entity_id):
        int_user_id = len(self.entities) + self.offset if entity_id not in self.entities else self.entities[entity_id]
        return int_user_id

    # if you need to change format of file (e.g. to pickle) do it in this method
    def _append_line(self, int_id, original_id):
        self.file_stream.write(str(original_id))
        self.file_stream.write(",")
        self.file_stream.write(str(int_id))
        self.file_stream.write("\n")

    def _open(self, dictionary_filename):
        file_stream = open(dictionary_filename, "w")
        return file_stream

    def close(self):
        self.file_stream.close()
        self.is_stream_open = False



class GraphBuilder:
    """
    A class that creates user&resource (e.g. user-repo graph for github, user graph for twitter and reddit) graph from events
    """
    def __init__(self, input_events):
        self.input_events_file_name = input_events
        self.event_counter = 0
        self.graph = nx.Graph()
        self.user_id_dict = IdDictionaryStream(input_events + "_users_id_dict.csv")
        self.resource_id_dict = IdDictionaryStream(input_events + "_resource_id_dict.csv", int_id_offset=2000000)
        self.input_events = open(input_events, "r")

    def update_graph(self, event):
        """
        Update graph using event_object
        :param event: dictionary of event object e.g. {"rootID": "bV4jnciU7e4r_zKD6YAehA", "actionType": "reply", "parentID": "bV4jnciU7e4r_zKD6YAehA", "nodeTime": "1487647690989", "nodeUserID": "poWidst6HLESGm-JWyYa9Q", "nodeID": "eOwlDjYw2V1X7OtC3fAPlg"}
        :return:
        """
        self.event_counter += 1
        # update ids
        user_id = self.user_id_dict.update_dictionary(event["nodeUserID"])
        resource_id = self.resource_id_dict.update_dictionary(event["nodeID"])
        root_resource_id = self.resource_id_dict.update_dictionary(event["rootID"])
        parent_resource_id = self.resource_id_dict.update_dictionary(event["parentID"])
        event_type = str(event["actionType"]).lower()
        try:
            event_time = int(self.resource_id_dict.update_dictionary(event["nodeTime"]))
        except:
            try:
                event_time = datetime.strptime(self.resource_id_dict.update_dictionary(event["nodeTime"]), "%Y-%m-%d %H:%M:%S")
            except:
                event_time = datetime.strptime(self.resource_id_dict.update_dictionary(event["nodeTime"]), "%Y-%m-%dT%H:%M:%SZ")
            event_time = time.mktime(event_time.timetuple())

        # add user node
        self.update_nodes_and_edges(user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time)


    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time):
        """
        Override this method for domain specific social network
        :param user_id:
        :param resource_id:
        :param root_resource_id:
        :param parent_resource_id:
        :param event_type:
        :param event_time:
        :return:
        """
        if not self.graph.has_node(user_id):
            self.graph.add_node(user_id, pop=0, isU=1)
        else:
            pass


    def finalize_graph(self):
        # finalize
        graph = self.graph
        number_of_users = len(self.user_id_dict.entities)
        number_of_resources = len(self.resource_id_dict.entities)
        self.input_events.close()
        self.user_id_dict.close()
        # pickle graph
        graph_file = open(self.input_events_file_name + "_graph.pickle", "wb")
        pickle.dump(graph, graph_file)
        graph_file.close()
        # clear
        self.event_counter = 0
        self.graph = None
        self.user_id_dict = None
        self.input_events = None

        return graph, number_of_users, number_of_resources

    def build_graph(self):
        if self.graph is None:
            self.__init__(self.input_events_file_name)
        objects = ijson.items(self.input_events, 'data.item')
        for event in objects:
            self.update_graph(event)
        graph, number_of_users, number_of_resources = self.finalize_graph()
        return graph, number_of_users, number_of_resources



def create_initial_state_files(input_json, graph_builder_class, initial_state_generators=None):
    graph_builder = graph_builder_class(input_json)
    graph, number_of_users, number_of_resources = graph_builder.build_graph()

    print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_resources, ", nodes ", len(graph.nodes()), ", edges", len(graph.edges())

    if initial_state_generators is None:
        users_ids = input_json + "_users_id_dict.csv"
        repos_ids = input_json + "_repos_id_dict.csv"
        graph_file_name = input_json + "_graph.pickle"

        state_file_content = {"meta":
            {
                "number_of_users": number_of_users,
                "number_of_resources": number_of_resources,
                "users_ids": users_ids,
                "repos_ids": repos_ids,
                "UR_graph_path": graph_file_name
            }
        }
        state_file_name = input_json + "_state.json"
        state_file = open(state_file_name, 'w')
        state_file.write(json.dumps(state_file_content))
        state_file.close()


if __name__ == "__main__":
    filename = "./data_sample.json" #sys.argv[1]
    graphBuilder = GraphBuilder(filename)
    graph, number_of_users, number_of_resources = graphBuilder.build_graph()
