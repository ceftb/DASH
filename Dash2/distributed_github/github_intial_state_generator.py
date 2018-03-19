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

    @staticmethod
    def loadProfiles(filename, number_of_partitions):
        profiles = []
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                id = rec["id"]
                freqs = rec["f"]
                profile = Profile(id, id, freqs)
                profiles.append(profile)
        partitions = []
        for i in range(0, number_of_partitions):
            partitions.append([])
        partition_size = int(len(profiles) / number_of_partitions)
        profile_counter = 0
        partition_file = None
        for profile in profiles:
            partition_index = profile_counter / partition_size
            partitions[partition_index].append(profile)
            if profile_counter % partition_size == 0:
                if partition_index != 0:
                    partition_file.write("]")
                    partition_file.close()
                partition_file = open(filename + "_" + str(partition_index), "w")
                partition_file.write("[\n")
            partition_file.write('{"id": ')
            partition_file.write(str(profile.int_id))
            partition_file.write(', "f": ')
            partition_file.write(json.dumps(profile.freqs))
            if (profile_counter + 1) % partition_size == 0:
                partition_file.write("}\n")
            else:
                partition_file.write("},\n")
            profile_counter += 1

        partition_file.write("]")
        partition_file.close()
        return profiles

    @staticmethod
    def partitionProfilesFile(filename, number_of_partitions):
        lenght = 0
        with open(filename, 'r') as f:
            records = ijson.items(f, 'item')
            for rec in records:
                lenght +=1
        f.close()

        partitions = []
        for i in range(0, number_of_partitions):
            partitions.append([])
        partition_size = int(lenght / number_of_partitions)
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
                if (profile_counter + 1) % partition_size == 0:
                    partition_file.write("}\n")
                else:
                    partition_file.write("},\n")
                profile_counter += 1

        partition_file.write("]")
        partition_file.close()


    @staticmethod
    def read_profile(row, users):
        event_type = row[1]
        user_id = row[2]
        repo_id = row[17]

    @staticmethod
    def countFreqs(filename):
        users_file = open("users.txt", "w")
        repos_file = open("repos.txt", "w")

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

        GithubStateLoader.print_to_file(user_hash_to_profile_map, users_file)
        GithubStateLoader.print_to_file(repo_hash_to_profile_map, repos_file)

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

            user_profile.update_freqs(repo_profile.int_id)
            repo_profile.update_freqs(user_profile.int_id)

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
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        while True:
            cmd = raw_input(
                "Press q to exit loader\n\tr to parse source data file and create user and repo profiles\n\tl to read profiles file into memory\n\tp to partition profiles file (not loaded in memory)\n")
            if cmd == "q":
                print("Exiting ...")
                break
            elif cmd == "r":
                print "Reading file and creating object profiles..."
                users, repos = GithubStateLoader.countFreqs(filename)
                print "users: ", len(users), ", repos: ", len(repos)
            elif cmd == "l":
                print "Loading object profiles ..."
                users = GithubStateLoader.loadProfiles(filename, 2)
                print "users: ", len(users)
            elif cmd == "p":
                print "Partitioning file ..."
                GithubStateLoader.partitionProfilesFile(filename, 2)
                print "partitioned"
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv
