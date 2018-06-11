import sys; sys.path.extend(['../../'])
import json
import csv
import ijson
import time
from datetime import datetime
import numpy as np
from scipy import sparse
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

'''
This class keeps embedding matrices fro users and repos. 
It allows to compute probabilities of using repos for a given user id.
'''
class EmbeddingCalculator(object):

    def __init__(self, embedding_file_name, strId2Xindex_file, UsimId2strId=None, strId2RsimId=None, UsimId2strId_file=None, strId2RsimId_file=None):
        # self.U - user embedding - matrix |U| x d
        # self.R - repo embedding - matrix |R| x d (d - number of embedding dimensions)
        # self.UsimId2Uindex - dictionary to convert integer simulation user ids to index number in U
        # self.Rindex2RsimId - dictionary to convert repo index index in R to simulation repo id. We need it because probabilities vector comes in pair with corresponding repo ids
        if UsimId2strId is None:
            UsimId2strId = self._load_UsimId2strId(UsimId2strId_file)
        if strId2RsimId is None:
            strId2RsimId = self._load_strId2RsimId_file(strId2RsimId_file)

        # X -> U and R - split adjacency matrix X into U - user embedding and R - repo embedding. Intermediate index dictionaries are created: Xindex2Uindex and Rindex2Xindex
        strId2Xindex = pickle.load(open(strId2Xindex_file, 'rb'))
        self.U, self.R, Xindex2Uindex, Rindex2Xindex, self.d = self._split_X_to_U_R(embedding_file_name, strId2Xindex)

        # initializing self.UsimId2Uindex
        # UsimId2strId* -> (not 1:1) strId2Xindex** -> Xindex2Uindex***
        self.UsimId2Uindex = {k: Xindex2Uindex[strId2Xindex[v]] if v in strId2Xindex else None for k, v in UsimId2strId.iteritems()}

        # initializing self.Rindex2simId
        # Rindex2Xindex*** -> (not 1:1) Xindex2strId** -> strId2RsimId*
        Xindex2strId = {v: k for k, v in strId2Xindex.iteritems()}
        self.Rindex2simId = {k: strId2RsimId[Xindex2strId[v]] if Xindex2strId[v] in strId2RsimId else None for k, v in Rindex2Xindex.iteritems()}

    def _split_X_to_U_R(self, embedding_file_name, strId2Xindex):
        X, d =self._load_X(embedding_file_name)

        number_of_repos_in_R = 0
        number_of_users_in_U = 0
        for strId, XIndex in strId2Xindex.iteritems():
            if str(strId).find("/") != -1: # if repo
                number_of_repos_in_R += 1
            else:
                number_of_users_in_U += 1
        U = np.zeros((int(number_of_users_in_U), int(d)), dtype=np.float)
        R = np.zeros((int(number_of_repos_in_R), int(d)), dtype=np.float)

        repo_row_index = 0
        user_row_index = 0
        Rindex2Xindex = {}
        Xindex2Uindex = {}
        for strId, XIndex in strId2Xindex.iteritems():
            if str(strId).find("/") != -1: # if repo
                Rindex2Xindex[repo_row_index] = XIndex
                R[repo_row_index, :] = X[int(XIndex), :]
                repo_row_index += 1
            else:
                Xindex2Uindex[XIndex] = user_row_index
                U[user_row_index, :] = X[int(XIndex), :]
                user_row_index += 1

        R = sparse.csr_matrix(R) # |R| x d matrix
        return U, R, Xindex2Uindex, Rindex2Xindex, d

    def _load_X(self, embedding_file_name):
        with open(embedding_file_name, 'r') as f:
            n, d = f.readline().strip().split()
            X = np.zeros((int(n), int(d)))
            for line in f:
                emb = line.strip().split()
                emb_fl = [float(emb_i) for emb_i in emb[1:]]
                X[int(emb[0]), :] = emb_fl
        f.close()
        return X, d

    def _load_UsimId2strId(self, UsimId2strId_file):
        return _load_id_dictionary(UsimId2strId_file, True)

    def _load_strId2RsimId_file(self, strId2RsimId_file):
        return _load_id_dictionary(strId2RsimId_file, False)

    def calculate_probabilities(self, user_id, probability_vector_size=10):
        max_probabilities_heap = []  # max size of the heap is probability_vector_size
        if user_id not in self.UsimId2Uindex or self.UsimId2Uindex[user_id] is None:
            return None
        user_emb_sparse = np.array(self.U[self.UsimId2Uindex[user_id], :])[np.newaxis].T
        prob_vector = self.R * user_emb_sparse
        prob_vector = prob_vector >= 0.05

        rows, cols = prob_vector.nonzero()
        if len(rows) == 0:
            return None
        print len(rows), ", ", len(cols)
        for row, col in zip(rows, cols): # col == 1
            value = prob_vector[row, col]
            if len(max_probabilities_heap) < probability_vector_size:
                heappush(max_probabilities_heap, (value, col))
                max = max_probabilities_heap[0][0]
            else:
                if value > max:
                    max = max_probabilities_heap[0][0]
                    heappop(max_probabilities_heap)
                    heappush(max_probabilities_heap, (value, row))

        result = {'ids': [], 'prob': []}
        while len(max_probabilities_heap) > 0:
            prob, id = heappop(max_probabilities_heap)
            if id in self.Rindex2simId:
                result['prob'].append(float(prob))
                result['ids'].append(self.Rindex2simId[id]) # convert repo_id_index to simulation id

        norm = np.linalg.norm(result['prob'], ord=1)
        result['prob'] = result['prob'] / norm
        return result

'''
Populates agent's decision data objects with repo probabilities. Probabilities either loaded from a .prob file 
(precomputed values of probability vectors) or from embedding files.
'''
def populate_embedding_probabilities(agents_decision_data, initial_state_meta_data, probability_vector_size = 10):
    embedding_files_data = initial_state_meta_data["embedding_files"]
    UsimId2strId = _load_id_dictionary(initial_state_meta_data["users_ids"], isSimId2strId=True)
    strId2RsimId = _load_id_dictionary(initial_state_meta_data["repos_ids"], isSimId2strId=False)
    for event_type in event_types:
        if event_type in embedding_files_data:
            if "probabilities_file" in embedding_files_data[event_type]:
                probabilities = pickle.load(embedding_files_data[event_type]["probabilities_file"])
                for _, decision_data in agents_decision_data.iteritems():
                    decision_data.embedding_probabilities[event_type] = probabilities[decision_data.id]
            else:
                calculator = EmbeddingCalculator(embedding_files_data[event_type]["file_name"], embedding_files_data[event_type]["dictionary"], UsimId2strId, strId2RsimId)
                for agent_id, decision_data in agents_decision_data.iteritems():
                    decision_data.embedding_probabilities[event_type] = calculator.calculate_probabilities(decision_data.id, probability_vector_size)

''' 
creates probability files (.prob files). Probabilities are computed from graph embedding.
'''
def compute_probabilities(state_file, destination_dir="./probabilities/", probability_vector_size = 10, users_batch_number=1, total_user_batches=1):
    initial_state_meta_data = read_state_file(state_file)
    embeddings_data = initial_state_meta_data["embedding_files"]
    UsimId2strId = _load_id_dictionary(initial_state_meta_data["users_ids"], isSimId2strId=True)
    strId2RsimId = _load_id_dictionary(initial_state_meta_data["repos_ids"], isSimId2strId=False)
    total_number_of_agents = len(UsimId2strId)
    total_number_of_repos = len(strId2RsimId)
    batch_size = total_number_of_agents / total_number_of_batches if total_number_of_agents % total_number_of_batches == 0 else total_number_of_agents / total_number_of_batches + 1
    min_index = (users_batch_number - 1) * batch_size
    max_index = users_batch_number * batch_size

    for event_type in event_types:
        if event_type in embeddings_data:
            all_probabilities = {}
            calculator = EmbeddingCalculator(embeddings_data[event_type]["file_name"], embeddings_data[event_type]["dictionary"], UsimId2strId, strId2RsimId)
            start_time = time.time()
            for index, agent_sim_id in enumerate(UsimId2strId.iterkeys()):
                if index >= min_index and index < max_index:
                    all_probabilities[agent_sim_id] = calculator.calculate_probabilities(agent_sim_id, probability_vector_size)
                    if index % 100 == 0:
                        end_time = time.time()
                        print "Agent ", index, " out of ", total_number_of_agents, " : ", 100.0 * float(index) / float(total_number_of_agents), "%, repos = ", total_number_of_repos, " time:", (end_time - start_time)
                        start_time = time.time()
            if total_user_batches > 1:
                output_file = open(destination_dir + event_type + "_" + str(users_batch_number) + ".prob", 'wb')
            else:
                output_file = open(destination_dir + event_type + ".prob", 'wb')
            pickle.dump(all_probabilities, output_file, protocol=2)
            output_file.close()



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
            "p to create probabilities file\n\t"
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
        elif cmd == "p":
            filename = sys.argv[1]
            batch_number = int(sys.argv[2])
            total_number_of_batches = int(sys.argv[3])
            print "computing probabilities from embedding ..."
            compute_probabilities(filename, users_batch_number=batch_number, total_user_batches=total_number_of_batches)
        else:
            print "Unrecognized command " + cmd + "\n"

