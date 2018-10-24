import sys; sys.path.extend(['../../'])
import networkx as nx
import json
import time
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

    @staticmethod
    def get_extention():
        return ".csv"

    def get_size(self):
        return len(self.entities)

    def close(self):
        self.file_stream.close()
        self.is_stream_open = False


class IdDictionaryInMemoryStream:
    """
    A stream that creates user or resource dictionary files
    """
    def __init__(self, dictionary_filename, int_id_offset=0):
        self.str_id_2_int_id = {}
        self.int_id_2_str_id = {}
        self.offset = int_id_offset
        self.dictionary_filename = dictionary_filename
        self.is_stream_open = True

    def update_dictionary(self, original_entity_id):
        if original_entity_id is not None and original_entity_id != "" and original_entity_id != "None":
            if original_entity_id not in self.str_id_2_int_id:
                int_entity_id = len(self.str_id_2_int_id) + self.offset
                self.str_id_2_int_id[original_entity_id] = int_entity_id
                self.int_id_2_str_id[int_entity_id] = original_entity_id
            else:
                int_entity_id = self.str_id_2_int_id[original_entity_id]

            return int_entity_id
        else:
            return None

    @staticmethod
    def get_extention():
        return ".pickle"

    def get_size(self):
        return len(self.str_id_2_int_id)

    def close(self):
        file_stream = open(self.dictionary_filename, "w")
        pickle.dump(self.int_id_2_str_id, file_stream)
        file_stream.close()
        self.is_stream_open = False


class GraphBuilder:
    """
    A class that creates user&resource (e.g. user-repo graph for github, user graph for twitter and reddit) graph from events
    """
    def __init__(self, input_events, event_types, event_type_list, dictionary_stream_cls=IdDictionaryStream):
        self.event_types = event_types
        self.event_type_list = event_type_list
        self.input_events_file_name = input_events
        self.event_counter = 0
        self.training_data_start_date = 0
        self.training_data_end_date = 1937955660
        self.graph = nx.Graph()
        self.user_id_dict = dictionary_stream_cls(input_events + "_users_id_dict" + dictionary_stream_cls.get_extention())
        self.resource_id_dict = dictionary_stream_cls(input_events + "_resource_id_dict" + dictionary_stream_cls.get_extention(), int_id_offset=2000000)
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
            event_time = int(event["nodeTime"])
        except:
            try:
                event_time = datetime.strptime(event["nodeTime"], "%Y-%m-%d %H:%M:%S")
            except:
                event_time = datetime.strptime(event["nodeTime"], "%Y-%m-%dT%H:%M:%SZ")
            event_time = time.mktime(event_time.timetuple())
        if self.training_data_start_date > event_time:
            self.training_data_start_date = event_time
        if self.training_data_end_date < event_time:
            self.training_data_end_date = event_time

        # add user node
        self.update_nodes_and_edges(user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time)


    def update_nodes_and_edges(self, user_id, resource_id, root_resource_id, parent_resource_id, event_type, event_time):
        if not self.graph.has_node(resource_id):
            self.graph.add_node(resource_id, pop=0, isU=0)

        event_index = self.event_types[event_type]
        if self.graph.has_node(user_id):
            self.graph.nodes[user_id]["r"] += 1.0
            self.graph.nodes[user_id]["ef"][event_index] += 1.0
        else:
            self.graph.add_node(user_id, isU=1, let=0)
            self.graph.nodes[user_id]["r"] = 1.0
            self.graph.nodes[user_id]["ef"] = [0.0] * len(self.event_type_list)
            self.graph.nodes[user_id]["ef"][event_index] += 1.0
            self.graph.nodes[user_id]["pop"] = 0  # init popularity
        if event_time > self.graph.nodes[user_id]["let"]:
            self.graph.nodes[user_id]["let"] = event_time

        if self.graph.has_edge(resource_id, user_id):
            self.graph.get_edge_data(resource_id, user_id)["weight"] += 1 #self.graph.add_edge(resource_id, user_id, weight=self.graph.get_edge_data(resource_id, user_id)['weight'] + 1)
        else:
            self.graph.add_edge(resource_id, user_id, own=0, weight=1)

    def finalize_graph(self):
        # finalize
        graph = self.graph
        number_of_users = self.user_id_dict.get_size()
        number_of_resources = self.resource_id_dict.get_size()
        self.input_events.close()
        self.user_id_dict.close()
        self.resource_id_dict.close()
        number_of_months = float((self.training_data_end_date - self.training_data_start_date) / (3600.0 * 24.0 * 30.0))
        for node_id in self.graph.nodes:
            if self.graph.nodes[node_id]["isU"] == 1:
                self.graph.nodes[node_id]["r"] /= number_of_months
                self.graph.nodes[node_id]['ef'] = [ef / number_of_months for ef in self.graph.nodes[node_id]['ef']]

        return graph, number_of_users, number_of_resources

    def pickle_graph(self):
        # pickle graph
        graph_file = open(self.input_events_file_name + "_graph.pickle", "wb")
        pickle.dump(self.graph, graph_file)
        graph_file.close()

    def clear_graph(self):
        # clear
        self.event_counter = 0
        self.graph = None
        self.user_id_dict = None
        self.input_events = None

    def build_graph(self):
        if self.graph is None:
            self.__init__(self.input_events_file_name, self.event_types, self.event_type_list)
        objects = ijson.items(self.input_events, 'data.item')
        for event in objects:
            self.update_graph(event)

        graph, number_of_users, number_of_resources = self.finalize_graph()
        self.pickle_graph()
        self.clear_graph()

        return graph, number_of_users, number_of_resources


def create_initial_state_files(input_json, graph_builder_class, event_types, event_type_list,
                               dictionary_stream_cls=IdDictionaryStream, initial_state_generators=None):
    print "Dictionary stream class: ", dictionary_stream_cls
    graph_builder = graph_builder_class(input_json, event_types, event_type_list, dictionary_stream_cls)
    graph, number_of_users, number_of_resources = graph_builder.build_graph()

    print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_resources, ", nodes ", len(graph.nodes()), ", edges", len(graph.edges())

    if initial_state_generators is None:
        users_ids = input_json + "_users_id_dict" + dictionary_stream_cls.get_extention()
        resource_ids = input_json + "_resource_id_dict" + dictionary_stream_cls.get_extention()
        graph_file_name = input_json + "_graph.pickle"

        state_file_content = {"meta":
            {
                "number_of_users": number_of_users,
                "number_of_resources": number_of_resources,
                "users_ids": users_ids,
                "resource_ids": resource_ids,
                "UR_graph_path": graph_file_name
            }
        }
        state_file_name = str(input_json).split(".json")[0] + "_state.json"
        state_file = open(state_file_name, 'w')
        state_file.write(json.dumps(state_file_content))
        state_file.close()


if __name__ == "__main__":
    filename = "./data_sample.json" #sys.argv[1]
    graphBuilder = GraphBuilder(filename, None, None)
    graph, number_of_users, number_of_resources = graphBuilder.build_graph()