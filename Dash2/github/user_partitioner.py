import time
import csv
import sys
import networkx as nx
import json
import metis


class GraphBuilder:
    """
    A class that creates user-repo graph from list events
    """

    def __init__(self, event_filter=None):
        self.graph = nx.Graph()
        self.events_to_accept = event_filter

    def update_graph(self, repo_id, user_id, event_type, event_subtype=None):
        if self.events_to_accept is None or event_type in self.events_to_accept:
            self.graph.add_node(repo_id, shared=0, isUser=0)
            self.graph.add_node(user_id, shared=0, isUser=1)
            if self.graph.has_edge(repo_id, user_id):
                self.graph.add_edge(repo_id, user_id, weight=self.graph.get_edge_data(repo_id, user_id)['weight'] + 1)
            else:
                self.graph.add_edge(repo_id, user_id, weight= 1)


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

    def close(self):
        self.user_dictionary.close()
        self.repo_dictionary.close()
        self.is_stream_open = False


def partition_graph(graph, number_of_partitions):
    if number_of_partitions == 1:
        for node in graph.nodes():
            graph.nodes[node]['partition'] = 0
        return set(), set()

    (edgecuts, parts) = metis.part_graph(graph, number_of_partitions)

    print "edgecuts ", edgecuts
    index_counter = 0
    for node in graph.nodes():
        graph.nodes[node]['partition'] = parts[index_counter]
        index_counter += 1

    shared_repos = set()
    shared_users = set()
    for u, v in graph.edges():
        if graph.nodes[u]['partition'] != graph.nodes[v]['partition']:  # cut edge
            if graph.nodes[u]['isUser'] == 0: # u in repos:
                shared_repos.add(u)
                graph.nodes[u]['shared'] = 1

            if graph.nodes[v]['isUser'] == 0: # v in repos:
                shared_repos.add(v)
                graph.nodes[v]['shared'] = 1

            if graph.nodes[u]['isUser'] == 1: # u in users:
                shared_users.add(u)
                graph.nodes[u]['shared'] = 1

            if graph.nodes[v]['isUser'] == 1: # v in users:
                shared_users.add(v)
                graph.nodes[v]['shared'] = 1

    return shared_repos, shared_users


def print_user_profiles(graph, users_filename, number_of_partitions, shared_repos):
    users_file = open(users_filename, 'w')
    users_parts_file = {}
    for i in range(0, number_of_partitions, 1):
        fp = open(users_filename + "_" + str(i), 'w')
        users_parts_file[i] = {'fp':fp, 'isFirst':True}

    isFirstLine = True
    for node in graph.nodes():
        if graph.nodes[node]['isUser'] == 1:
            fp = users_parts_file[graph.nodes[node]['partition']]['fp']
            _print_json_profile(graph, node, fp, shared_repos, users_parts_file[graph.nodes[node]['partition']]['isFirst'])
            users_parts_file[graph.nodes[node]['partition']]['isFirst'] = False

            _print_json_profile(graph, node, users_file, shared_repos, isFirstLine)
            isFirstLine = False

    for i in range(0, number_of_partitions, 1):
        fp = users_parts_file[i]['fp']
        fp.write("]")
        fp.close()

    users_file.write("]")
    users_file.close()

def _print_json_profile(graph, user_node, fp, shared_repos, isFirst=False):
    profile_data = {'id': user_node}
    for neighbour in graph.neighbors(user_node):
        edge_weight = graph.get_edge_data(user_node, neighbour)['weight']
        isSharedRepo = 2 if neighbour in shared_repos else 1
        profile_data[neighbour] = {'f':edge_weight, 'c':isSharedRepo}
    if not isFirst:
        fp.write(",\n")
    else:
        fp.write("[")
    fp.write(json.dumps(profile_data))


def build_graph_from_csv(csv_event_log_file, user_dict_file=None, repo_dict_file=None, event_filter=["PushEvent", "IssueCommentEvent", "PullRequestEvent", "PullRequestReviewCommentEvent"]):
    user_repo_graph_builder = GraphBuilder(event_filter = event_filter)
    ids_dictionary_stream = IdDictionaryStream(csv_event_log_file + "_users_id_dict.csv", csv_event_log_file + "_repos_id_dict.csv", event_filter = event_filter)

    with open(csv_event_log_file, "rb") as csvfile:
        datareader = csv.reader(csvfile)
        counter = 0
        for row in datareader:
            if counter != 0:
                event_type = row[1]
                if event_filter is None or event_type in event_filter:
                    user_id, repo_id = ids_dictionary_stream.update_dictionary(row[2], row[3])
                    user_repo_graph_builder.update_graph(repo_id, user_id, event_type)
            counter += 1
            if counter % 1000000 == 0:
                print "line: " + str(counter)
        print counter

    csvfile.close()
    ids_dictionary_stream.close()

    return user_repo_graph_builder.graph, len(ids_dictionary_stream.users), len(ids_dictionary_stream.repos)

if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        filename = sys.argv[1]
    else:
        filename = "tmp.txt"
    while True:
        cmd = raw_input(
            "Press q to exit loader\n\tg to test networkX graph\n")
        if cmd == "q":
            print("Exiting ...")
            break
        elif cmd == "g":
            print "graph test"
            start_time = time.time()

            G, users, repos = build_graph_from_csv(filename)
            print "User-repo graph constructed. Users ", len(users), ", repos ", len(repos), ", nodes ", len(G.nodes()), ", edges", len(G.edges())

            shared_repos, shared_users = partition_graph(G, 10)
            print "shared repos ", len(shared_repos), ", shared users ", len(shared_users)

            print "printing graph..."
            print_user_profiles(G, filename, 10, shared_repos)

            end_time = time.time()
            print "Time ", end_time - start_time, " sec."
        else:
            print "Unrecognized command " + cmd + "\n"


