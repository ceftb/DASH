import sys; sys.path.extend(['../../'])
import networkx as nx
import json
import os.path
import time
import numpy as np
import cPickle as pickle
import ijson



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
        self.input_events = input_events
        self.event_counter = 0
        self.graph = nx.Graph()
        self.user_id_dict = IdDictionaryStream(input_events + "_users_id_dict.csv")
        self.resource_id_dict = IdDictionaryStream(input_events + "_resource_id_dict.csv")
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

        # add user node
        if not self.graph.has_node(user_id):
            self.graph.add_node(user_id, pop=0, isU=1)
        else:
            pass




    def finalize_graph(self):
        # finalize:
        graph = self.graph
        self.input_events.close()
        self.user_id_dict.close()
        # clear:
        self.event_counter = 0
        self.graph = None
        self.user_id_dict = None
        self.input_events = None

        return graph

    def build_graph(self):
        if self.graph is None:
            self.__init__(self.input_events)
        objects = ijson.items(self.input_events, 'data.item')
        for event in objects:
            self.update_graph(event)
        graph = self.finalize_graph()
        return graph


def get_action_type_and_index(event, type_dictionary):
    """
    :param event: a dictionary with key "actionType". Action type is converted to string and index of the event
    :param type_dictionary: a dictionary with event types mapped to their indexes
    :return:
    """
    return str(event["actionType"]), type_dictionary[str(event["actionType"])]


if __name__ == "__main__":
    filename = "./data_sample.json" #sys.argv[1]
    graphBuilder = GraphBuilder(filename)
    graph = graphBuilder.build_graph()
