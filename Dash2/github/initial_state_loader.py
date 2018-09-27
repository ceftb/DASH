import sys; sys.path.extend(['../../'])
import json
import os.path
import time
import numpy as np
import cPickle as pickle
from distributed_event_log_utils import load_id_dictionary, collect_unique_user_event_pairs
from user_repo_graph_utils import build_graph_from_csv, partition_graph, print_user_profiles, print_graph,\
print_users_neighborhood_sizes, subsample, subsample2

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

def build_state_from_event_log(input_event_log, number_of_user_partitions=1, state_file_name=None, embedding_files=None,
                               training_data_weight=1.0, initial_condition_data_weight=1.0, initial_state_generators=None):
    graph, number_of_users, number_of_repos = build_graph_from_csv(input_event_log,
                                                                   event_filter=None,
                                                                   training_data_weight=training_data_weight,
                                                                   initial_condition_data_weight=initial_condition_data_weight)
    original_input_event_log = input_event_log
    print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_repos, ", nodes ", len(graph.nodes()), ", edges", len(graph.edges())

    if initial_state_generators is None:
        G =graph
        partition_graph(G, number_of_user_partitions)
        print "printing graph..."
        print_user_profiles(G, input_event_log + "_users.json", number_of_user_partitions)
        graph_file_name = input_event_log + "_UR_graph.pickle"
        print_graph(G, graph_file_name)
        users_neighborhood_sizes_file = input_event_log + "_users_neighborhood_sizes.pickle"
        print_users_neighborhood_sizes(G, users_neighborhood_sizes_file)

        users_file = input_event_log + "_users.json"
        repos_file = input_event_log + "_repos.json"
        users_ids = input_event_log + "_users_id_dict.csv"
        repos_ids = input_event_log + "_repos_id_dict.csv"

        state_file_content = {"meta":
            {
                "number_of_users": number_of_users,
                "number_of_repos": number_of_repos,
                "users_file": users_file,
                "repos_file": repos_file,
                "users_ids": users_ids,
                "repos_ids": repos_ids,
                "number_of_partitions": number_of_user_partitions,
                "event_rate_model_file": "",
                "UR_graph_path": graph_file_name,
                "users_neighborhood_sizes_file": users_neighborhood_sizes_file
            }
        }
        state_file_name = input_event_log + "_state.json"
        state_file = open(state_file_name, 'w')
        state_file.write(json.dumps(state_file_content))
        state_file.close()
    else:
        run_number = 0
        for state_generator in initial_state_generators:
            for sample in range(0, state_generator.number_of_graph_samples):
                input_event_log = original_input_event_log + str(run_number)
                run_number += 1
                print "Updating graph ..."
                G = state_generator.update(graph)
                number_of_users = state_generator.max_number_of_user_nodes
                number_of_repos = len(G.nodes) - state_generator.max_number_of_user_nodes
                print "Updated graph has ", len(G.nodes), "nodes and ", len(G.edges), " edges."

                partition_graph(G, number_of_user_partitions)

                print "printing graph..."
                print_user_profiles(G, input_event_log + "_users.json", number_of_user_partitions)
                graph_file_name = input_event_log + "_UR_graph.pickle"
                print_graph(G, graph_file_name)
                users_neighborhood_sizes_file = input_event_log + "_users_neighborhood_sizes.pickle"
                print_users_neighborhood_sizes(G, users_neighborhood_sizes_file)

                users_file = input_event_log + "_users.json"
                repos_file = input_event_log + "_repos.json"
                users_ids = original_input_event_log + "_users_id_dict.csv"
                repos_ids = original_input_event_log + "_repos_id_dict.csv"

                state_file_content = {"meta":
                    {
                        "number_of_users": number_of_users,
                        "number_of_repos": number_of_repos,
                        "users_file": users_file,
                        "repos_file": repos_file,
                        "users_ids": users_ids,
                        "repos_ids": repos_ids,
                        "number_of_partitions": number_of_user_partitions,
                        "event_rate_model_file": "",
                        "UR_graph_path": graph_file_name,
                        "users_neighborhood_sizes_file": users_neighborhood_sizes_file
                    }
                }
                state_file_name = input_event_log + "_state.json"
                state_file = open(state_file_name, 'w')
                state_file.write(json.dumps(state_file_content))
                state_file.close()
    return None

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

class InitialStateSampleGenerator(object):

    def __init__(self, max_depth, max_number_of_user_nodes, number_of_neighborhoods, number_of_graph_samples):
        self.max_depth = max_depth if max_depth % 2 == 1 else max_depth + 1 # must be odd number
        self.max_number_of_user_nodes = max_number_of_user_nodes
        self.number_of_neighborhoods = number_of_neighborhoods
        self.number_of_graph_samples = number_of_graph_samples

    def update(self, G):
        sub_sample_G = subsample(G, self.max_depth, self.max_number_of_user_nodes,
                                 number_of_start_nodes=self.number_of_neighborhoods)
        return sub_sample_G

class InitialStateSimpleSampleGenerator(object):

    def __init__(self, max_number_of_user_node, number_of_graph_sampless):
        self.max_number_of_user_nodes = max_number_of_user_node
        self.number_of_graph_samples = number_of_graph_sampless

    def update(self, G):
        sub_sample_G = subsample2(G, self.max_number_of_user_nodes)
        return sub_sample_G

'''
This class keeps embedding mgatrices fro users and repos. 
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

        #R = sparse.csr_matrix(R) # |R| x d matrix
        U = U.transpose()
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
        return load_id_dictionary(UsimId2strId_file, True)

    def _load_strId2RsimId_file(self, strId2RsimId_file):
        return load_id_dictionary(strId2RsimId_file, False)

    def calculate_probabilities(self, user_id, probability_vector_size=10, cut_off_threshold = 0.99):
        topk_probabilities = []  # k is probability_vector_size
        if user_id not in self.UsimId2Uindex or self.UsimId2Uindex[user_id] is None:
            return None
        prob_vector = np.dot(self.R, self.U[:, self.UsimId2Uindex[user_id]])

        prob_vector_sum = 0.0
        for index in range(0, probability_vector_size, 1):
            row = prob_vector.argmax()
            topk_probabilities.append((prob_vector[row], row))
            prob_vector_sum += prob_vector[row]
            if prob_vector_sum > cut_off_threshold: # stop searching for max probability already have enough
                break
            prob_vector[row] = 0
        # tail is for random choice, coded with -1
        topk_probabilities.append((1.0 - prob_vector_sum, -1))

        result = {'ids': [], 'prob': []}
        for prob, id in topk_probabilities:
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
def populate_embedding_probabilities(agents_decision_data, embedding_path, truncation_coef = 1.0):
    for event_type in event_types:
        prob_file_path = str(embedding_path) + event_type + ".prob"
        if os.path.isfile(prob_file_path):
            print "Event type: ", event_type, ", loading probabilities from .prob files (.prob - probabilities are precomputed in advance)."
            prob_file = open(prob_file_path, 'rb')
            probabilities = pickle.load(prob_file); prob_file.close()
            for _, decision_data in agents_decision_data.iteritems():
                if decision_data.id in probabilities:
                    decision_data.embedding_probabilities[event_type] = probabilities[decision_data.id]
                    # truncate vector
                    new_prob_vect_len = int(float(len(decision_data.embedding_probabilities[event_type]["ids"])) * float(truncation_coef))
                    if truncation_coef != 1.0 and new_prob_vect_len > 2.0:
                        decision_data.embedding_probabilities[event_type]["ids"] = decision_data.embedding_probabilities[event_type]["ids"][:new_prob_vect_len + 1]
                        decision_data.embedding_probabilities[event_type]["prob"] = decision_data.embedding_probabilities[event_type]["prob"][:new_prob_vect_len + 1]
                        norm = np.linalg.norm(decision_data.embedding_probabilities[event_type]["prob"], ord=1)
                        decision_data.embedding_probabilities[event_type]["prob"] = decision_data.embedding_probabilities[event_type]["prob"] / norm

''' 
creates probability files (.prob files). Probabilities are computed from graph embedding.
'''
def compute_probabilities(state_file, embedding_path, users_batch_number=1, total_user_batches=1, event2users=None):
    initial_state_meta_data = read_state_file(state_file)
    embedding_path = embedding_path #initial_state_meta_data["embedding_path"]
    UsimId2strId = load_id_dictionary(initial_state_meta_data["users_ids"], isSimId2strId=True)
    strId2RsimId = load_id_dictionary(initial_state_meta_data["repos_ids"], isSimId2strId=False)
    total_number_of_agents = len(UsimId2strId)

    def _time(index, start_time):
        if index % 1000 == 0:
            end_time = time.time()
            print "Agent ", index, " out of ", total_number_of_agents, " : ",           100.0 * float(index) / float(
                total_number_of_agents), "%, ", " time:", (end_time - start_time)
            start_time = time.time()
        return start_time

    users_neighborhood_size = pickle.load(open(initial_state_meta_data["users_neighborhood_sizes_file"], "rb"))

    for event_type in event_types:
        emb_file_path = str(embedding_path) + event_type + ".emb"
        if os.path.isfile(emb_file_path):
            id_file_path = str(embedding_path) + event_type + "_nodeID_gf.pickle"
            all_probabilities = {}
            calculator = EmbeddingCalculator(emb_file_path, id_file_path, UsimId2strId, strId2RsimId)
            start_time = time.time()
            if event2users is None:
                for index, agent_sim_id in enumerate(UsimId2strId.iterkeys()):
                    probability_vector_size = users_neighborhood_size[agent_sim_id] if agent_sim_id in users_neighborhood_size else 10
                    all_probabilities[agent_sim_id] = calculator.calculate_probabilities(agent_sim_id, probability_vector_size)
                    start_time = _time(index, start_time)
            else:
                total_number_of_agents = len(event2users[event_type])
                min_index = (users_batch_number - 1) * int(total_number_of_agents / total_number_of_batches)
                max_index = users_batch_number * int(total_number_of_agents / total_number_of_batches) if users_batch_number != total_user_batches else total_number_of_agents
                #print "min: ", min_index, ", max : ", max_index, " total agents: ", total_number_of_agents
                for index in range(min_index, max_index, 1):
                    user_id = event2users[event_type][index]
                    probability_vector_size = 2 * users_neighborhood_size[user_id] if user_id in users_neighborhood_size else 10
                    all_probabilities[user_id] = calculator.calculate_probabilities(user_id, probability_vector_size)
                    start_time = _time(index, start_time)

            if total_user_batches > 1:
                output_file = open(str(embedding_path) + event_type + "_" + str(users_batch_number) + ".prob", 'wb')
            else:
                output_file = open(str(embedding_path) + event_type + ".prob", 'wb')
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

def gather_prob_files(src_dir, dst_dir):
    for event_type in event_types:
        probabilities = {}
        index = 1
        file_path = src_dir + event_type + "_" + str(index) + ".prob"
        while os.path.isfile(file_path):
            prob_file = open(file_path, 'rb')
            part_prob = pickle.load(prob_file)
            prob_file.close()
            probabilities.update(part_prob)
            index += 1
            file_path = src_dir + event_type + "_" + str(index) + ".prob"
        if index > 1:
            output_file = open(dst_dir + event_type + ".prob", "wb")
            pickle.dump(probabilities, output_file, protocol=2)

if __name__ == "__main__":
    while True:
        cmd = raw_input(
            "Press q to exit loader\n\t"
            "l to load objects from profiles file and load them into memory\n\t"
            "p to create probabilities file\n\t"
            "g to gather (merge) probability files\n\t"
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
        elif cmd == "p":
            state_filename = sys.argv[1]
            embedding_path = sys.argv[2]
            events_filename = sys.argv[3]
            batch_number = int(sys.argv[4])
            total_number_of_batches = int(sys.argv[5])
            event2users = collect_unique_user_event_pairs(events_filename, load_id_dictionary(read_state_file(state_filename)["users_ids"], isSimId2strId=False))
            print "computing probabilities from embedding ..."
            compute_probabilities(state_file=state_filename, embedding_path=embedding_path, users_batch_number=batch_number, total_user_batches=total_number_of_batches,
                                  event2users=event2users)
        elif cmd == "g":
            src_dir = sys.argv[1] # must have '/' in the end
            dst_dir = sys.argv[2] # must have '/' in the end
            print "Gathering all probability files togather"
            gather_prob_files(src_dir, dst_dir)
            print "Done"
        else:
            print "Unrecognized command " + cmd + "\n"

