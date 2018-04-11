import sys; sys.path.extend(['../../'])
from intial_state_loader import GithubStateLoader

def count_repos_and_agents(user_hash_to_profile_map, repo_hash_to_profile_map):

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



if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3 or len(sys.argv) == 1:
        filename = "output.csv" #sys.argv[1]
        while True:
            cmd = raw_input(
                "Press q to exit loader\n\tr to parse source data file and create user and repo profiles\n\t"
                "l to load objects from profiles file and load them into memory\n\tp to partition profiles file (not loaded in memory)\n\t"
                "s to load state file\n\tm to merge output log files\n\tt to translate ids\n\t")
            if cmd == "q":
                print("Exiting ...")
                break
            elif cmd == "r":
                print "Reading CSV file and creating object profiles (*_users.json and *_repos.json) ..."
                users, repos = GithubStateLoader.convert_csv_to_json_profiles(filename)
                # FIXME: format of profile was changed, need to update counter function
                # count_repos_and_agents(users, repos)
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
                meta = GithubStateLoader.read_state_file(filename)
                print "users: ", meta["number_of_users"], ", repos: ", meta["number_of_repos"]
            elif cmd == "m":
                print "Merging output log files ..."
                meta = GithubStateLoader.merge_log_file(["0-0-1_event_log_file.txt", "0-0-2_event_log_file.txt"], "output.csv", "timestamp,event,user_id,repo_id\n")
                print "Merged."
            elif cmd == "t":
                print "Translating user and repo ids ..."
                meta = GithubStateLoader.trnaslate_user_and_repo_ids_in_event_log(even_log_file=filename,
                                                                                  output_file_name="translated.csv",
                                                                                  users_ids_file="./data_jan_2017_json/data_jan_2017.csv_users_id_dict.csv",
                                                                                  repos_ids_file="./data_jan_2017_json/data_jan_2017.csv_repos_id_dict.csv")
                print "Merged."
            else:
                print "Unrecognized command " + cmd + "\n"
    else:
        print 'incorrect arguments: ', sys.argv

