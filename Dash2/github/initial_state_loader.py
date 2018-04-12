import sys; sys.path.extend(['../../'])
import json
import csv
import ijson
import datetime

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
    # profile = {"id":234, "234":{"h":234432, "f":2, "c":23}, "234":{"h":234432, "f":2, "c":4}, ... }
    # "f" - frequency of use
    # "c" - number of other repos/users connected/associated with this user/repo
    # "h" - id hash, not used in profiles file.
    '''

    @staticmethod
    def build_state_from_event_log(input_event_log, number_of_hosts=1):
        user_hash_to_profile_map, repo_hash_to_profile_map = GithubStateLoader.convert_csv_to_json_profiles(input_event_log)
        number_of_users = len(user_hash_to_profile_map)
        number_of_repos = len(repo_hash_to_profile_map)
        users_file = input_event_log + "_users.json"
        repos_file = input_event_log + "_repos.json"
        users_ids = input_event_log + "_users_id_dict.csv"
        repos_ids = input_event_log + "_repos_id_dict.csv"
        GithubStateLoader.partition_profiles_file(users_file, number_of_hosts, number_of_users)
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
        counter = 0
        for row in datareader:
            if counter != 0:
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
            else:
                line_counter = 0
                for itm in row:
                    output_file.write(itm)
                    if line_counter == (len(row) - 1):
                        output_file.write("\n")
                    else:
                        output_file.write(",")
                    line_counter += 1
            counter += 1
            if counter % 1000000 == 0:
                print "line: " + str(counter)
        print counter

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

    @staticmethod
    def partition_profiles_file(filename, number_of_partitions, number_of_records_in_file = None):
        if number_of_records_in_file is None:
            number_of_records_in_file = 0
            with open(filename, 'r') as f:
                records = ijson.items(f, 'item')
                for rec in records:
                    number_of_records_in_file +=1
            f.close()

        if number_of_records_in_file < number_of_partitions:
            raise ValueError('Received: number_of_records_in_file < number_of_partitions. Must be number_of_records_in_file >= number_of_partitions')

        partition_size = number_of_records_in_file / number_of_partitions
        rest = number_of_records_in_file % number_of_partitions
        record_counter = 0
        partition_file = None
        prev_partition_index = -1

        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                if record_counter < (partition_size + 1) * rest:
                    partition_index = record_counter / (partition_size + 1)
                else:
                    partition_index = rest + (record_counter - (partition_size + 1) * rest) / partition_size
                # if new partition
                if prev_partition_index != partition_index:
                    if partition_index != 0: # skip for first file
                        partition_file.write("]")
                        partition_file.close()
                    partition_file = open(filename + "_" + str(partition_index), "w")
                    partition_file.write("[")
                else:
                    partition_file.write(",\n")
                partition_file.write(json.dumps(rec))
                record_counter += 1
                prev_partition_index = partition_index
            f.close()
        partition_file.write("]")
        partition_file.close()

    @staticmethod
    def convert_csv_to_json_profiles(filename):
        users_file = open(filename + "_users.json", "w")
        repos_file = open(filename + "_repos.json", "w")
        users_id_dict = open(filename + "_users_id_dict.csv", "w")
        users_id_dict.write("src_id, sim_id\n")
        repos_id_dict = open(filename + "_repos_id_dict.csv", "w")
        repos_id_dict.write("src_id, sim_id\n")

        user_hash_to_profile_map = {}
        repo_hash_to_profile_map = {}

        max_time_limit = datetime.datetime.strptime( "2017-01-31T23:59:55Z", "%Y-%m-%dT%H:%M:%SZ" )
        min_time_limit = datetime.datetime.strptime( "2014-01-31T23:59:55Z", "%Y-%m-%dT%H:%M:%SZ" )

        with open(filename, "rb") as csvfile:
            datareader = csv.reader(csvfile)
            counter = 0
            for row in datareader:
                if counter != 0:
                    GithubStateLoader.read_csv_line(row, user_hash_to_profile_map, users_id_dict, repos_id_dict,
                                                    repo_hash_to_profile_map, min_time_limit, max_time_limit)
                counter += 1
                if counter % 1000000 == 0:
                    print "line: " + str(counter)
                    print "users: ", len(user_hash_to_profile_map)
                    print "repos: ", len(repo_hash_to_profile_map)
            print counter

        GithubStateLoader.print_to_file(user_hash_to_profile_map, users_file, repo_hash_to_profile_map)
        GithubStateLoader.print_to_file(repo_hash_to_profile_map, repos_file, user_hash_to_profile_map)

        csvfile.close()
        users_file.close()
        repos_file.close()
        users_id_dict.close()
        repos_id_dict.close()

        return user_hash_to_profile_map, repo_hash_to_profile_map

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


    @staticmethod
    def read_csv_line(row, user_map, users_id_dict, repos_id_dict, repo_map, min_time, max_time):
        event_time = max_time # datetime.datetime.strptime( row[0], "%Y-%m-%dT%H:%M:%SZ" )
        if event_time <= max_time and event_time >= min_time:
            event_type = row[1]
            user_id = row[2]
            if len(row) > 4:
                repo_id = row[17]
            else:
                repo_id = row[3]

            user_profile = GithubStateLoader.get_profile_and_update_map_if_new(user_map, user_id, users_id_dict)
            repo_profile = GithubStateLoader.get_profile_and_update_map_if_new(repo_map, repo_id, repos_id_dict)

            GithubStateLoader.update_freqs(user_profile, repo_profile, user_id, repo_id)

    @staticmethod
    def get_profile_and_update_map_if_new(map, id, id_dict):
        id_hash = hash(id)
        if not map.has_key(id_hash): # new entry
            map[id_hash] = {"id":len(map)} #Profile(int_id=len(map), freqs={})
            id_dict.write(str(id))
            id_dict.write(",")
            id_dict.write(str(map[id_hash]["id"]))
            id_dict.write("\n")
        return map[id_hash]

    @staticmethod
    def print_to_file(profiles, profiles_file, other_entity_hash_to_profile_map):
        number_of_items = len(profiles)
        item_counter = 0
        profiles_file.write("[\n")
        for profile in profiles.itervalues():
            # user
            for key, frq_dict in profile.iteritems():
                if key != "id":
                    degree = len(other_entity_hash_to_profile_map[frq_dict["h"]]) - 1
                    frq_dict["c"] = degree
                    #frq_dict["c"].extend(other_entity_hash_to_profile_map[frq_dict["h"]].iterkeys()) # generates too big file, turned off.
                    frq_dict.pop('h', None)
            item_counter += 1
            profiles_file.write(json.dumps(profile))
            for key, frq_dict in profile.iteritems():
                if key != "id":
                    frq_dict.clear()
            if item_counter != number_of_items:
                profiles_file.write(",\n")
        profiles_file.write("]")

    @staticmethod
    def update_freqs(user_profile, repo_profile, user_id, repo_id):
        # user
        if not user_profile.has_key(repo_profile["id"]):
            user_profile[repo_profile["id"]] = {}
            user_profile[repo_profile["id"]]["h"] = hash(repo_id)
            user_profile[repo_profile["id"]]["f"] = 0 # frequencies
            #user_profile[repo_profile["id"]]["c"] = []  # list of connections # generates too big file, turned off
        user_profile[repo_profile["id"]]["f"] += 1
        # repo
        if not repo_profile.has_key(user_profile["id"]):
            repo_profile[user_profile["id"]] = {}
            repo_profile[user_profile["id"]]["h"] = hash(user_id)
            repo_profile[user_profile["id"]]["f"] = 0  # frequencies
            #repo_profile[user_profile["id"]]["c"] = []  # list of connections # generates too big file, turned off
        repo_profile[user_profile["id"]]["f"] += 1


if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        filename = sys.argv[1]
        while True:
            cmd = raw_input(
                "Press q to exit loader\n\tr to parse source data file and create user and repo profiles\n\t"
                "l to load objects from profiles file and load them into memory\n\tp to partition profiles file (not loaded in memory)\n\t"
                "s to load state file\n")
            if cmd == "q":
                print("Exiting ...")
                break
            elif cmd == "r":
                print "Reading CSV file and creating object profiles (*_users.json and *_repos.json) ..."
                users, repos = GithubStateLoader.convert_csv_to_json_profiles(filename)
                print "users: ", len(users), ", repos: ", len(repos)
            elif cmd == "l":
                print "Loading objects from profiles file..."
                objects = []
                appender = lambda rec: objects.append(rec)
                GithubStateLoader.load_profiles_from_file(filename, appender)
                print "objects loaded: ", len(objects)
            elif cmd == "p":
                print "Partitioning file ..."
                number_of_partitions = raw_input("Enter number of partitions:\n")
                GithubStateLoader.partition_profiles_file(filename, int(number_of_partitions), 2646461)
                print "partitioned"
            elif cmd == "s":
                print "Reading state file ..."
                n_users, n_repos = GithubStateLoader.read_state_file(filename)
                print "users: ", n_users, ", repos: ", n_repos
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv

