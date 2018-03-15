import sys; sys.path.extend(['../../'])
import time
import json
import csv
import struct
from kazoo.client import KazooClient
from Dash2.github.git_user_agent import GitUserAgent


class GithubStateLoader(object):

    @staticmethod
    def loadUsersAndRepos(filename):
        users_file = open("users.txt", "w")
        repos_file = open("repos.txt", "w")

        user_hash_to_profile_map = {}
        repo_hash_to_profile_map = {}

        with open(filename, "rb") as csvfile:
            datareader = csv.reader(csvfile)
            counter = 0
            for row in datareader:
                GithubStateLoader.read_line(row, user_hash_to_profile_map, repo_hash_to_profile_map)
                counter += 1
                if counter % 1000000 == 0 :
                    print "line: " + str(counter)
                    print "users: ", len(user_hash_to_profile_map)
                    print "repos: ", len(repo_hash_to_profile_map)
            print counter

        GithubStateLoader.print_to_file(user_hash_to_profile_map, repo_hash_to_profile_map, users_file)
        GithubStateLoader.print_to_file(repo_hash_to_profile_map, user_hash_to_profile_map, repos_file)

        users_file.close()
        repos_file.close()

    @staticmethod
    def read_line(row, user_map, repo_map):
        event_type = row[1]
        user_id = row[2]
        repo_id = row[17]

        user_profile = GithubStateLoader.get_profile_and_update_map_if_new(user_map, user_id)
        repo_profile = GithubStateLoader.get_profile_and_update_map_if_new(repo_map, repo_id)

        user_profile.update_freqs(repo_id)
        repo_profile.update_freqs(user_id)

    @staticmethod
    def get_profile_and_update_map_if_new(map, id):
        id_hash = hash(id)
        if not map.has_key(id_hash): # new user
            map[id_hash] = Profile(id=id, intid=len(map), freqs={})
        return map[id_hash]

    @staticmethod
    def print_to_file(profiles, freq_items_profiles, profiles_file):
        for profile_id_hash, profile in profiles.iteritems():
            profiles_file.write(str(profile.intid))
            profiles_file.write(": ")
            for freq_item_id_hash, freq in profile.freqs.iteritems():
                profiles_file.write(str(freq_items_profiles[freq_item_id_hash].intid))
                profiles_file.write(" ")
                profiles_file.write(str(freq))
                profiles_file.write("; ")
            profiles_file.write("\n")

class Profile:
    def __init__(self, id=None, intid=0, freqs={}):
        self.id = id
        self.intid = intid
        self.freqs = freqs

    def update_freqs(self, id):
        id_hash = hash(id)
        if not self.freqs.has_key(id_hash):  # new repo for this user
            self.freqs[id_hash] = 0
        self.freqs[id_hash] += 1

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

if __name__ == "__main__":
    print "Reading file ..."
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        GithubStateLoader.loadUsersAndRepos(filename)
        while True:
            cmd = raw_input(
                "Press q to exit loader\n")
            if cmd == "q":
                print("Exiting ...")
                break
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv

