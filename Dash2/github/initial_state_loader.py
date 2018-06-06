import sys; sys.path.extend(['../../'])
import json
import csv
import ijson
from datetime import datetime
import numpy as np
import cPickle as pickle
from distributed_event_log_utils import _load_id_dictionary
from heapq import heappush, heappop
from user_partitioner import build_graph_from_csv, partition_graph, print_user_profiles
from distributed_event_log_utils import event_types

'''
state file structure:
{
        "meta":  {
                    "number_of_users": 10,
                    "number_of_repos": 20,
                    "users_file": "users.json"
                    ... other properties
                    }
}

profiles file structure (used for both users and repos - relationship is symmetrical) :
[
        {"id":234, "r":21, "ef": [12,24,0,1,0], "234":{"f":2, "c":23}, "234":{"f":2, "c":4}, ... },
        {"id":123, "r":321, "ef": [12,24,0,1,0], "1222":{"f":2, "c":23}, "233":{"f":2, "c":4}, ... }
]
# profile = {"id":234, "r":321, "ef": [12,24,0,1,0], "234":{ "f":2, "c":23}, "234":{"f":2, "c":4}, ... }
# "f" - frequency of use
# "c" - number of other repos/users connected/associated with this user/repo
# "r" - event rate per month
# "ef" - event frequencies
'''

def build_state_from_event_log(input_event_log, number_of_user_partitions=1, state_file_name=None, embedding_files=None):
    G, number_of_users, number_of_repos = build_graph_from_csv(input_event_log)
    print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_repos, ", nodes ", len(G.nodes()), ", edges", len(G.edges())

    shared_repos, shared_users = partition_graph(G, number_of_user_partitions)
    print "shared repos ", len(shared_repos), ", shared users ", len(shared_users)

    print "printing graph..."
    print_user_profiles(G, input_event_log + "_users.json", number_of_user_partitions, shared_repos)

    users_file = input_event_log + "_users.json"
    repos_file = input_event_log + "_repos.json"
    users_ids = input_event_log + "_users_id_dict.csv"
    repos_ids = input_event_log + "_repos_id_dict.csv"

    if embedding_files is None or len(embedding_files) == 0:
        embedding_files = ""

    state_file_content = {"meta":
        {
            "number_of_users": number_of_users,
            "number_of_repos": number_of_repos,
            "users_file": users_file,
            "repos_file": repos_file,
            "users_ids": users_ids,
            "repos_ids": repos_ids,
            "number_of_partitions": number_of_user_partitions,
            "embedding_files": embedding_files,
            "event_rate_model_file": ""
        }
    }
    state_file_name = input_event_log + "_state.json" if state_file_name is None else state_file_name
    state_file = open(state_file_name, 'w')
    state_file.write(json.dumps(state_file_content))
    state_file.close()
    return state_file_content["meta"]

def read_state_file(filename):
    raw_data = json.load(open(filename))
    return raw_data["meta"]

def load_profiles(filename, profile_handler):
    with open(filename, 'r') as f:
        while True:
            try:
                profile = pickle.load(f)
                profile_handler(profile)
            except EOFError:
                break
        f.close()



class EmbeddingCalculator(object):

    def __init__(self, embedding_file_name, embdg_ids_dictionary_file, int_to_str_ids_map):
        self.X, self.node_ids_map, self.all_repos_indexes = self._load_embedding(embedding_file_name, embdg_ids_dictionary_file)
        self.int_to_str_ids_map = int_to_str_ids_map

    def calculate_probabilities(self, user_id, probability_vector_size = 10):
        user_str_id = self.int_to_str_ids_map[user_id]
        if user_str_id in self.node_ids_map:
            embedding_id = self.node_ids_map[user_str_id]
            probabilities = self._calculate_top_probabilities(embedding_id, self.X, self.node_ids_map, self.all_repos_indexes, probability_vector_size)
            return probabilities
        else:
            return None

    def _load_embedding(self, file_name, embdg_ids_dictionary_file):
        with open(file_name, 'r') as f:
            n, d = f.readline().strip().split()
            X = np.zeros((int(n), int(d)))
            for line in f:
                emb = line.strip().split()
                emb_fl = [float(emb_i) for emb_i in emb[1:]]
                X[int(emb[0]), :] = emb_fl
        f.close()
        node_ids_map = pickle.load(open(embdg_ids_dictionary_file, 'rb'))

        all_repos_indexes = []
        for node_id, node_embd_int_id in node_ids_map.iteritems():
            if str(node_id).find("/") != -1:
                all_repos_indexes.append(node_embd_int_id)

        return X, node_ids_map, all_repos_indexes

    def _calculate_top_probabilities(self, user_id, embedding, node_ids_map, all_repos_indexes,
                                     number_of_top_probabilities=10):
        X = embedding
        user_emb = X[user_id]
        max_probabilities_heap = []  # max size of the heap is number_of_top_probabilities
        for repo_index in all_repos_indexes:
            repo_emb = X[repo_index]
            value = np.dot(user_emb, repo_emb)
            if len(max_probabilities_heap) < number_of_top_probabilities:
                heappush(max_probabilities_heap, value)
            else:
                if value > max_probabilities_heap[0]:
                    heappop(max_probabilities_heap)
                    heappush(max_probabilities_heap, value)
        # normalize
        result = []
        total_sum = 0
        while len(max_probabilities_heap) > 0:
            val = heappop(max_probabilities_heap)
            result.append(val)
            total_sum += val
        for i in range(1, len(result)):
            result[i] = result[i] / total_sum

        return result


def populate_embedding_probabilities(agents_decision_data, simulation_user_ids_dictionary_file, embedding_files_data, probability_vector_size = 10):
    int_to_str_ids_map = _load_id_dictionary(simulation_user_ids_dictionary_file)
    for event_type in event_types:
        if event_type in embedding_files_data:
            if "probabilities_file" in embedding_files_data[event_type]:
                probabilities = pickle.load(embedding_files_data[event_type]["probabilities_file"])
                for _, decision_data in agents_decision_data.iteritems():
                    decision_data.embedding_probabilities[event_type] = probabilities[decision_data.id]
            else:
                calculator = EmbeddingCalculator(embedding_files_data[event_type]["file_name"], embedding_files_data[event_type]["dictionary"], int_to_str_ids_map)
                for agent_id, decision_data in agents_decision_data.iteritems():
                    decision_data.embedding_probabilities[event_type] = calculator.calculate_probabilities(decision_data.id, probability_vector_size)

def populate_event_rate(agents, model_file):
    # load model from model_file
    loaded_model = pickle.load(open(model_file, 'rb'))

    for agent in agents:
        event_rate = agent.decision_data.event_rate
        focus = len(agent.decision_data.all_known_repos)
        if event_rate is not None and focus is not None and focus != 0:
            X = np.array([[float(event_rate) / 30.0, focus]])  # the first feature is previous pace and the second feature is focus
            new_rate = loaded_model.predict(X)
            agent.decision_data.event_rate = new_rate


if __name__ == "__main__":
    while True:
        cmd = raw_input(
            "Press q to exit loader\n\t"
            "l to load objects from profiles file and load them into memory\n\t"
            "e to load embedding into memory\n\t"
            "s to load state file\n")
        if cmd == "q":
            print("Exiting ...")
            break
        elif cmd == "l":
            filename = sys.argv[1]
            print "Generating state file for 1 partition ..."
            build_state_from_event_log(filename, 1)
        elif cmd == "s":
            filename = sys.argv[1]
            print "Reading state file ..."
            n_users, n_repos = read_state_file(filename)
            print "users: ", n_users, ", repos: ", n_repos
        elif cmd == "e":
            filename = sys.argv[1]
            print "Reading embedding file ..."
            embedding_ids_file = sys.argv[2]
            sim_ids_file = sys.argv[3]
            embedding_calculator = EmbeddingCalculator(filename, embedding_ids_file, sim_ids_file)
            prob = embedding_calculator.calculate_probabilities(10)
            print "done: ", prob

        else:
            print "Unrecognized command " + cmd + "\n"

