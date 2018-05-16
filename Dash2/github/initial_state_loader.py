import sys; sys.path.extend(['../../'])
import json
import csv
import ijson
import datetime
from user_partitioner import build_graph_from_csv, partition_graph, print_user_profiles

class GithubStateLoader(object):

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
            {"id":234, "234":{"f":2, "c":23}, "234":{"f":2, "c":4}, ... },
            {"id":123, "1222":{"f":2, "c":23}, "233":{"f":2, "c":4}, ... }
    ]
    # profile = {"id":234, "234":{ "f":2, "c":23}, "234":{"f":2, "c":4}, ... }
    # "f" - frequency of use
    # "c" - number of other repos/users connected/associated with this user/repo

    '''

    @staticmethod
    def build_state_from_event_log(input_event_log, number_of_hosts=1):
        G, number_of_users, number_of_repos = build_graph_from_csv(input_event_log)
        print "User-repo graph constructed. Users ", number_of_users, ", repos ", number_of_repos, ", nodes ", len(G.nodes()), ", edges", len(G.edges())

        shared_repos, shared_users = partition_graph(G, number_of_hosts)
        print "shared repos ", len(shared_repos), ", shared users ", len(shared_users)

        print "printing graph..."
        print_user_profiles(G, input_event_log + "_users.json", number_of_hosts, shared_repos)

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
                "is_partitioning_needed": "False"
            }
        }
        state_file = open(input_event_log + "_state.json", 'w')
        state_file.write(json.dumps(state_file_content))
        state_file.close()
        return state_file_content["meta"]


    @staticmethod
    def merge_log_file(file_names, output_file_name, header_line=None, sort_chronologically=False):
        if sort_chronologically:
            print "Under development, work in progress ..."
        else:
            output_file = open(output_file_name, 'w')
            if header_line is not  None:
                output_file.write(header_line)
                output_file.write("\n")

            for filename in file_names:
                input_log = open(filename, "r")
                datareader = input_log.readlines()
                for line in datareader:
                    output_file.write(line)
                input_log.close()
            output_file.close()

    @staticmethod
    def trnaslate_user_and_repo_ids_in_event_log(even_log_file, output_file_name, users_ids_file, repos_ids_file):
        input_file = open(even_log_file, 'r')
        output_file = open(output_file_name, 'w')
        users_map = GithubStateLoader.load_id_dictionary(users_ids_file)
        repos_map = GithubStateLoader.load_id_dictionary(repos_ids_file)

        datareader = csv.reader(input_file)
        for row in datareader:
            user_id = int(row[2])
            repo_id = int(row[3])
            if users_map.has_key(user_id):
                src_user_id = users_map[user_id]
            else:
                src_user_id = user_id
            if repos_map.has_key(repo_id):
                src_repo_id = repos_map[repo_id]
            else:
                src_repo_id = repo_id
            output_file.write(row[0])
            output_file.write(",")
            output_file.write(row[1])
            output_file.write(",")
            output_file.write(str(src_user_id))
            output_file.write(",")
            output_file.write(str(src_repo_id))
            output_file.write("\n")

        input_file.close()
        output_file.close()


    @staticmethod
    def read_state_file(filename):
        raw_data = json.load(open(filename))
        return raw_data["meta"]


    @staticmethod
    def load_profiles_from_file(filename, profile_handler):
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                profile_handler(rec)
            f.close()

    ####################################
    # util methods below
    ####################################

    @staticmethod
    def load_id_dictionary(dictionary_file_name):
        dict_file = open(dictionary_file_name, "r")
        datareader = csv.reader(dict_file)
        ids_map = {}
        counter = 0
        for row in datareader:
            if counter != 0:
                src_id = row[0]
                target_id = row[1]
                ids_map[int(target_id)] = src_id
            counter += 1
        dict_file.close()
        return ids_map

if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        filename = sys.argv[1]
        while True:
            cmd = raw_input(
                "Press q to exit loader\n\t"
                "l to load objects from profiles file and load them into memory\n\t"
                "s to load state file\n")
            if cmd == "q":
                print("Exiting ...")
                break
            elif cmd == "l":
                print "Loading objects from profiles file..."
                objects = []
                appender = lambda rec: objects.append(rec)
                GithubStateLoader.load_profiles_from_file(filename, appender)
                print "objects loaded: ", len(objects)
            elif cmd == "s":
                print "Reading state file ..."
                n_users, n_repos = GithubStateLoader.read_state_file(filename)
                print "users: ", n_users, ", repos: ", n_repos
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv

