import time
import csv
import sys
import networkx as nx
import json
import metis
import pickle
from distributed_event_log_utils import event_types, event_types_indexes
from datetime import datetime


class GraphBuilder:
    """
    A class that creates user-repo graph from list events
    """

    def __init__(self, event_filter=None):
        self.graph = nx.Graph()
        self.events_to_accept = event_filter

    def update_graph(self, repo_id, user_id, event_type, event_time, event_subtype=None):
        if self.events_to_accept is None or event_type in self.events_to_accept:
            if not self.graph.has_node(repo_id):
                self.graph.add_node(repo_id, pop=0, isU=0)

            event_index = event_types_indexes[event_type]
            if self.graph.has_node(user_id):
                self.graph.nodes[user_id]["r"] = self.graph.nodes[user_id]["r"] + 1
                self.graph.nodes[user_id]["ef"][event_index] += 1
            else:
                self.graph.add_node(user_id, shared=0, isU=1, r=1)
                self.graph.nodes[user_id]["ef"] = [0] * len(event_types)
                self.graph.nodes[user_id]["ef"][event_index] += 1
                self.graph.nodes[user_id]["pop"] = 0 # init popularity
            self.graph.nodes[user_id]["let"] = event_time

            if self.graph.has_edge(repo_id, user_id):
                self.graph.add_edge(repo_id, user_id, weight=self.graph.get_edge_data(repo_id, user_id)['weight'] + 1)
            else:
                self.graph.add_edge(repo_id, user_id, own=0, weight= 1)
                self.graph.get_edge_data(repo_id, user_id)['ef'] = [0] * len(event_types)
            self.graph.get_edge_data(repo_id, user_id)['ef'][event_index] += 1

            # popularity of repos
            if event_type == "ForkEvent" or event_type == "WatchEvent":
                self.graph.nodes[repo_id]["pop"] += 1

    def compute_users_popularity_and_event_rate(self, creator2repos, number_of_months):
        '''
        Computation of user popularity is done after the whole graph is constructed, the same is true for event rate.
        :param creator2repos:
        :return:
        '''
        for user_id, own_repos in creator2repos.iteritems():
            popularity = 0
            for repo in own_repos:
                popularity += self.graph.nodes[repo]["pop"]
                if not self.graph.has_edge(repo, user_id):
                    self.graph.add_edge(repo, user_id, weight=0)
                self.graph.get_edge_data(repo, user_id)['own'] = 1
            self.graph.nodes[user_id]["pop"] = popularity
            self.graph.nodes[user_id]["r"] /= float(number_of_months)

    @staticmethod
    def get_users_neighborhood_size(graph):
        user_to_neighborhoos_size_map = {}
        for node in graph.nodes:
            if graph.nodes[node]["isU"] == 1:
                neighbors = graph.neighbors(node)
                neighbors_counter = 0
                for _ in neighbors:
                    neighbors_counter += 1
                user_to_neighborhoos_size_map[node] = neighbors_counter
        return  user_to_neighborhoos_size_map


class IdDictionaryStream:
    """
    A stream that creates user and repo dictionary files
    """
    MAGIC_NUMBER = 20000000

    def __init__(self, user_dictionary_filename, repo_dictionary_filename, event_filter=None):
        self.users = {}
        self.repos = {}
        self.user_dictionary = open(user_dictionary_filename, "w")
        self.repo_dictionary = open(repo_dictionary_filename, "w")
        self.user_dictionary.write("src_id, sim_id\n")
        self.repo_dictionary.write("src_id, sim_id\n")
        self.is_stream_open = True
        self.events_to_accept = event_filter
        self.user_creator_to_repos = {} # dictionary of lists
        self.creator2repos = None

    def update_dictionary(self, original_user_id, original_repo_id):
        hash_user_id = hash(original_user_id)
        hash_repo_id = hash(original_repo_id)
        int_user_id, int_repo_id = self._conver_to_conseq_int_ids(hash_user_id, hash_repo_id)

        if hash_user_id not in self.users:
            self.users[hash_user_id] = int_user_id
            self._append_line(self.user_dictionary, int_user_id, original_user_id)
        if hash_repo_id not in self.repos:
            self.repos[hash_repo_id] = int_repo_id
            self._append_line(self.repo_dictionary, int_repo_id, original_repo_id)

        usr_repo = str(original_repo_id).split("/")
        if usr_repo[0] not in self.user_creator_to_repos:
            self.user_creator_to_repos[usr_repo[0]] = []
        self.user_creator_to_repos[usr_repo[0]].append(original_repo_id)

        return int_user_id, int_repo_id

    def _conver_to_conseq_int_ids(self, user_id, repo_id):
        int_user_id = len(self.users) if user_id not in self.users else self.users[user_id]
        int_repo_id = len(self.repos) + IdDictionaryStream.MAGIC_NUMBER if repo_id not in self.repos else self.repos[repo_id]
        return int_user_id, int_repo_id

    def _append_line(self, id_dict, int_id, original_id):
        id_dict.write(str(original_id))
        id_dict.write(",")
        id_dict.write(str(int_id))
        id_dict.write("\n")

    def getCreator2reposMap(self):
        if self.creator2repos is None:
            creator2repos = {}
            for owner, repo_list in self.user_creator_to_repos.iteritems(): # owner, repo_list are string ids
                hash_user_id = hash(owner)
                if hash_user_id in self.users:
                    if self.users[hash_user_id] not in creator2repos:
                        creator2repos[self.users[hash_user_id]] = []
                    for repo in repo_list:
                        hash_repo_id = hash(repo)
                        if hash_repo_id in self.repos:
                            creator2repos[self.users[hash_user_id]].append(self.repos[hash_repo_id])
            self.creator2repos = creator2repos
        return self.creator2repos

    def close(self):
        self.user_dictionary.close()
        self.repo_dictionary.close()
        self.is_stream_open = False


def partition_graph(graph, number_of_partitions):
    if number_of_partitions == 1:
        for node in graph.nodes():
            graph.nodes[node]['prt'] = 0
            graph.nodes[node]['shrd'] = 0
        return

    (edgecuts, parts) = metis.part_graph(graph, number_of_partitions)

    print "edgecuts ", edgecuts
    index_counter = 0
    for node in graph.nodes():
        graph.nodes[node]['prt'] = parts[index_counter]
        index_counter += 1
        graph.nodes[node]['shrd'] = 0

    for u, v in graph.edges():
        if graph.nodes[u]['prt'] != graph.nodes[v]['prt']:  # cut edge
            if graph.nodes[u]['isU'] == 0: # u in repos:
                graph.nodes[u]['shrd'] = 1

            if graph.nodes[v]['isU'] == 0: # v in repos:
                graph.nodes[v]['shrd'] = 1

            if graph.nodes[u]['isU'] == 1: # u in users:
                graph.nodes[u]['shrd'] = 1

            if graph.nodes[v]['isU'] == 1: # v in users:
                graph.nodes[v]['shrd'] = 1


def print_user_profiles(graph, users_filename, number_of_partitions):
    users_parts_file = {}
    for i in range(0, number_of_partitions, 1):
        fp = open(users_filename + "_" + str(i), 'w')
        users_parts_file[i] = {'fp':fp}

    for node in graph.nodes():
        if graph.nodes[node]['isU'] == 1:
            fp = users_parts_file[graph.nodes[node]['prt']]['fp']
            _print_user_profile(graph, node, fp)

    for i in range(0, number_of_partitions, 1):
        fp = users_parts_file[i]['fp']
        fp.close()

    pickle.dump(graph, open("UR_graph.pickle", "wb"))
    pickle.dump(GraphBuilder.get_users_neighborhood_size(graph), open("users_neighborhood_size.pickle", "wb"))


def _print_user_profile(graph, user_node, fp):
    profile_object = {'id': user_node, 'r': graph.nodes[user_node]["r"], 'ef':graph.nodes[user_node]["ef"]}
    profile_object["own"] = [] #owned_repos[user_node] if owned_repos is not None and user_node in owned_repos else []
    profile_object["pop"] = graph.nodes[user_node]["pop"]
    profile_object["all_repos"] = {}
    profile_object["let"] = graph.nodes[user_node]["let"]
    for neighbour in graph.neighbors(user_node):
        edge_weight = graph.get_edge_data(user_node, neighbour)['weight']
        isOwnRepo = True if graph.get_edge_data(user_node, neighbour)['own'] == 1 else False
        isSharedRepo = 2 if graph.nodes[neighbour]['shrd'] == 1 else 1 #isSharedRepo = 2 if neighbour in shared_repos else 1
        profile_object["all_repos"][neighbour] = {'f':edge_weight, 'c':isSharedRepo}
        if isOwnRepo:
            profile_object["own"].append(neighbour)
    fp.write(pickle.dumps(profile_object))


def build_graph_from_csv(csv_event_log_file, number_of_months, event_filter=None):
    user_repo_graph_builder = GraphBuilder(event_filter = event_filter)
    ids_dictionary_stream = IdDictionaryStream(csv_event_log_file + "_users_id_dict.csv", csv_event_log_file + "_repos_id_dict.csv", event_filter = event_filter)

    with open(csv_event_log_file, "rb") as csvfile:
        datareader = csv.reader(csvfile)
        counter = 0
        for row in datareader:
            if counter != 0:
                event_type = row[1]
                if event_type == "CreateEvent" and len(row) == 5 and row[4] == "repository":
                    event_type = "CreateEvent/new"
                try:
                    event_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                except:
                    event_time = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")
                event_time = time.mktime(event_time.timetuple())
                if event_filter is None or event_type in event_filter:
                    user_id, repo_id = ids_dictionary_stream.update_dictionary(row[2], row[3])
                    user_repo_graph_builder.update_graph(repo_id, user_id, event_type, event_time)
            counter += 1
            if counter % 1000000 == 0:
                print "line: " + str(counter)
        print counter

    csvfile.close()
    user_repo_graph_builder.compute_users_popularity_and_event_rate(ids_dictionary_stream.getCreator2reposMap(), number_of_months)
    ids_dictionary_stream.close()

    return user_repo_graph_builder.graph, len(ids_dictionary_stream.users), len(ids_dictionary_stream.repos)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        number_of_partitions = int(sys.argv[2])
    else:
        filename = "tmp.txt"
        number_of_partitions = 2

    while True:
        cmd = raw_input(
            "Press q to exit loader\n\tt to test networkX graph partitioning\n\tp to partition graph\n")
        if cmd == "q":
            print("Exiting ...")
            break
        elif cmd == "t":
            print "graph test"
            start_time = time.time()

            G, users, repos = build_graph_from_csv(filename)
            print "User-repo graph constructed. Users ", len(users), ", repos ", len(repos), ", nodes ", len(G.nodes()), ", edges", len(G.edges())

            partition_graph(G, number_of_partitions)
            #print "shared repos ", len(shared_repos), ", shared users ", len(shared_users)

            print "printing graph..."
            print_user_profiles(G, filename, 10)

            end_time = time.time()
            print "Time ", end_time - start_time, " sec."
        elif cmd == "p":
            print "Partitioning users from ", filename, " into ", number_of_partitions, " partitions ..."
            start_time = time.time()

            G, number_of_users, number_of_repos = build_graph_from_csv(filename)
            print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_repos, ", nodes ", len(G.nodes()), ", edges", len(G.edges())
            partition_graph(G, number_of_partitions)
            #print "shared repos ", len(shared_repos), ", shared users ", len(shared_users)

            print "printing graph..."
            print_user_profiles(G, filename + "_users.json", number_of_partitions)

            users_file = filename + "_users.json"
            repos_file = filename + "_repos.json"
            users_ids = filename + "_users_id_dict.csv"
            repos_ids = filename + "_repos_id_dict.csv"

            state_file_content = {"meta":
                {
                    "number_of_users": number_of_users,
                    "number_of_repos": number_of_repos,
                    "users_file": users_file,
                    "repos_file": repos_file,
                    "users_ids": users_ids,
                    "repos_ids": repos_ids,
                    "is_partitioning_needed": "False"
                }
            }
            state_file = open(filename + "_state.json", 'w')
            state_file.write(json.dumps(state_file_content))
            state_file.close()

            end_time = time.time()
            print "Time ", end_time - start_time, " sec."
        else:
            print "Unrecognized command " + cmd + "\n"


