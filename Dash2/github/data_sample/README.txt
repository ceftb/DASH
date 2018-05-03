####### RUNNING EXPERIMENT ######
To start the zk_github_state_experiment.py make sure to choose data sample to instantiate initial state. To do so in ZkGithubStateTrial class change

input_event_log = "./data_sample/data_sample.csv" # data_sample.csv is a cumulative event list

Then run the controller process:
python zk_github_state_experiment.py

and worker process:
python ../core/dash_worker.py

The controller process by default is run in interactive mode, so follow screen instructions to start the experiment.

######## INITIAL STATE FILES ####

First run will create initial state files. Those include:
data_sample/data_sample.csv_repos.json # json repo profiles, contains frequencies of use and other statistic
data_sample/data_sample.csv_repos_id_dict.csv # integer id to original id map for repos
data_sample/data_sample.csv_state.json # state meta information
data_sample/data_sample.csv_users.json # json user profiles, contains frequencies of use and other statistic
data_sample/data_sample.csv_users.json_0 # json user profiles for dash worker #0
data_sample/data_sample.csv_users.json_1 # json user profiles for dash worker #1
data_sample/data_sample.csv_users_id_dict.csv # integer id to original id map for users

Creation of initial state files may take some time at startup (~20 min for month of data). It is done on the controller process.
Once experiment is complete, outputs of each trial can be found in data_sample.csv_output_trial_<trial_number>.csv


State file stucture:
{"meta": 
	{ 
	"number_of_users": 2,
	"number_of_repos": 4,
	"users_file": "./data_sample/data_sample.csv_users.json",
	"repos_file": "./data_sample/data_sample.csv_repos.json",
	"users_ids": "./data_sample/data_sample.csv_users_id_dict.csv",
	"repos_ids": "./data_sample/data_sample.csv_repos_id_dict.csv",
	"is_partitioning_needed": "True"
	}
}

Additional information on how to install and configure zookeeper can be found in github/README.txt


