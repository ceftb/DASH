import sys; sys.path.extend(['../../'])
import json
import csv
import ijson
import pickle
from datetime import datetime
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
            {"id":234, "r":21, "ef": [12,24,0,1,0], "234":{"f":2, "c":23}, "234":{"f":2, "c":4}, ... },
            {"id":123, "r":321, "ef": [12,24,0,1,0], "1222":{"f":2, "c":23}, "233":{"f":2, "c":4}, ... }
    ]
    # profile = {"id":234, "r":321, "ef": [12,24,0,1,0], "234":{ "f":2, "c":23}, "234":{"f":2, "c":4}, ... }
    # "f" - frequency of use
    # "c" - number of other repos/users connected/associated with this user/repo
    # "r" - event rate per month
    # "ef" - event frequencies
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
    def read_state_file(filename):
        raw_data = json.load(open(filename))
        return raw_data["meta"]

    @staticmethod
    def load_profiles(filename, profile_handler):
        with open(filename, 'r') as f:
            while True:
                try:
                    profile = pickle.load(f)
                    profile_handler(profile)
                except EOFError:
                    break
            f.close()


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

