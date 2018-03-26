import sys; sys.path.extend(['../../'])
import time
import json
import csv
import struct
from kazoo.client import KazooClient
from Dash2.github.git_user_agent import GitUserAgent
from dateutil.parser import parse
import ijson

class GithubStateLoader(object):

    '''
    state file structure:
    {
            "totals": [
                        {
                        "number_of_users": 10,
                        "number_of_repos": 20
                        }
                    ],
            "users": [{
                     "id": 232,
                     "f": {
                            "123":1,
                            "452":2
                         }
                     }],
            "repos": [{
                     "id": 232,
                     "f": {
                            "123":1,
                            "452":2
                         }
                     },
                    {
                     "id": 232,
                     "f": {
                            "123":1,
                            "452":2
                         }
                     }
                    ]
    }
    '''
    @staticmethod
    def loadStateFile(filename):
        user_profiles = []
        repo_profiles = []
        number_of_users = None
        number_of_repos = None
        with open(filename, 'r') as f:
            records = ijson.items(f, 'totals.item')
            for rec in records:
                number_of_users = rec['number_of_users']
                number_of_repos = rec['number_of_repos']
            f.close()
        # users
        with open(filename, 'r') as f:
            records = ijson.items(f, 'users.item')
            for rec in records:
                id = rec["id"]
                freqs = rec["f"]
                profile = Profile(id, id, freqs)
                user_profiles.append(profile)
            f.close()
        # repos
        with open(filename, 'r') as f:
            records = ijson.items(f, 'repos.item')
            for rec in records:
                id = rec["id"]
                freqs = rec["f"]
                profile = Profile(id, id, freqs)
                repo_profiles.append(profile)
            f.close()

        return user_profiles, repo_profiles

    @staticmethod
    def loadProfilesFile(filename):
        profiles = []
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                id = rec["id"]
                freqs = rec["f"]
                profile = Profile(id, id, freqs)
                profiles.append(profile)
            f.close()

        return profiles

    @staticmethod
    def loadIterativelyProfilesFile(filename, profile_handler):
        profile = Profile(None, None, None)
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                profile.id = int(rec["id"])
                profile.freqs = rec["f"]
                profile_handler(profile)
            f.close()

    @staticmethod
    def partitionProfilesFile(filename, number_of_partitions):
        number_of_records_in_file = 0
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                number_of_records_in_file +=1
        f.close()

        partition_size = int(float(number_of_records_in_file) / float(number_of_partitions) + 1.0)
        profile_counter = 0
        partition_file = None

        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                partition_index = profile_counter / partition_size
                if profile_counter % partition_size == 0:
                    if partition_index != 0:
                        partition_file.write("]")
                        partition_file.close()
                    partition_file = open(filename + "_" + str(partition_index), "w")
                    partition_file.write("[\n")
                partition_file.write('{"id": ')
                partition_file.write(str(rec["id"]))
                partition_file.write(', "f": ')
                partition_file.write(json.dumps(rec["f"]))
                profile_counter += 1
                if profile_counter == number_of_records_in_file or profile_counter % partition_size == 0:
                    partition_file.write("}\n")
                else:
                    partition_file.write("},\n")
            f.close()
        partition_file.write("]")
        partition_file.close()


    @staticmethod
    def read_profile(row, users):
        event_type = row[1]
        user_id = row[2]
        repo_id = row[17]

    @staticmethod
    def countFreqs(filename):
        users_file = open(filename + "_users.json", "w")
        repos_file = open(filename + "_repos.json", "w")

        user_hash_to_profile_map = {}
        repo_hash_to_profile_map = {}

        max_time_limit = parse("2017-01-31T23:59:55Z")
        min_time_limit = parse("2014-01-31T23:59:55Z")

        with open(filename, "rb") as csvfile:
            datareader = csv.reader(csvfile)
            counter = 0
            for row in datareader:
                if counter != 0:
                    GithubStateLoader.read_src_line(row, user_hash_to_profile_map, repo_hash_to_profile_map, min_time_limit, max_time_limit)
                counter += 1
                if counter % 1000000 == 0:
                    print "line: " + str(counter)
                    print "users: ", len(user_hash_to_profile_map)
                    print "repos: ", len(repo_hash_to_profile_map)
            print counter

        #'''
        # to user this counter need to change user_profile.update_freqs(repo_profile.int_id) to user_profile.update_freqs(hash(repo_profile.id))
        counter = 0
        counter2 = 0
        for repo_hash, repo_profile in repo_hash_to_profile_map.iteritems():
            if len(repo_profile.freqs) == 1:
                counter2 += 1
                for user_hash, fr in repo_profile.freqs.iteritems():
                    if len(user_hash_to_profile_map[user_hash].freqs) == 1:
                        counter += 1
        print "Number of users with only one repo (visa versa) ", counter
        print "Number of repos with only one user ", counter2

        counter = 0
        for u_hash, user_profile in user_hash_to_profile_map.iteritems():
            if len(user_profile.freqs) == 1:
                counter += 1
        print "Number of users with only one repo ", counter
        #'''

        GithubStateLoader.print_to_file(user_hash_to_profile_map, users_file)
        GithubStateLoader.print_to_file(repo_hash_to_profile_map, repos_file)

        csvfile.close()
        users_file.close()
        repos_file.close()

        return user_hash_to_profile_map, repo_hash_to_profile_map

    @staticmethod
    def read_src_line(row, user_map, repo_map, min_time, max_time):
        event_time = max_time #parse(row[0])
        if event_time <= max_time and event_time >= min_time:
            event_type = row[1]
            user_id = row[2]
            repo_id = row[17]

            user_profile = GithubStateLoader.get_profile_and_update_map_if_new(user_map, user_id, hash(user_id))
            repo_profile = GithubStateLoader.get_profile_and_update_map_if_new(repo_map, repo_id, hash(repo_id))

            user_profile.update_freqs(hash(repo_profile.id))
            repo_profile.update_freqs(hash(user_profile.id))

    @staticmethod
    def get_profile_and_update_map_if_new(map, id, id_hash):
        if not map.has_key(id_hash): # new entry
            map[id_hash] = Profile(id, int_id=len(map), freqs={})
        return map[id_hash]

    @staticmethod
    def print_to_file(profiles, profiles_file):

        number_of_items = len(profiles)
        item_counter = 0
        profiles_file.write("[\n")
        for profile_id_hash, profile in profiles.iteritems():
            item_counter += 1
            profiles_file.write('{"id": ')
            profiles_file.write(str(profile.int_id))
            profiles_file.write(', "f": ')
            profiles_file.write(json.dumps(profile.freqs))
            if item_counter == number_of_items:
                profiles_file.write("}\n")
            else:
                profiles_file.write("},\n")
        profiles_file.write("]")


class Profile:
    def __init__(self, id, int_id, freqs):
        self.id = id
        self.int_id = int_id
        self.freqs = freqs

    def update_freqs(self, id_hash):
        if not self.freqs.has_key(id_hash):
            self.freqs[id_hash] = 0
        self.freqs[id_hash] += 1

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        filename = sys.argv[1]
        while True:
            cmd = raw_input(
                "Press q to exit loader\n\tr to parse source data file and create user and repo profiles\n\t"
                "l to read state file into memory\n\tlp to read profiles file into memory\n\tp to partition profiles file (not loaded in memory)\n")
            if cmd == "q":
                print("Exiting ...")
                break
            elif cmd == "r":
                print "Reading file and creating object profiles..."
                users, repos = GithubStateLoader.countFreqs(filename)
                print "users: ", len(users), ", repos: ", len(repos)
            elif cmd == "l":
                print "Loading object profiles from state file..."
                users, repos = GithubStateLoader.loadStateFile(filename)
                print "users: ", len(users), ", repos: ", len(repos)
            elif cmd == "lp":
                print "Loading object profiles from profiles file..."
                users = GithubStateLoader.loadProfilesFile(filename)
                print "users: ", len(users)
            elif cmd == "p":
                print "Partitioning file ..."
                GithubStateLoader.partitionProfilesFile(filename, int(sys.argv[2]))
                print "partitioned"
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv
