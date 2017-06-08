import subprocess
import threading
import numbers
import numpy
from trial import Trial
from parameter import Range
from dash import DASHAgent

# An experiment consists of a varying condition and for each condition a number of trials.
# trial.py shows how the trials can be customized, and phish_experiment.py gives an example of the experiment harness.


class Experiment(object):
    def __init__(self, trial_class=Trial, independent=None, dependent=None, exp_data={}, num_trials=3,
                 file_output=None, hosts=None, experiment_file="/users/blythe/webdash/Dash2/pass_experiment.py",
                 user="blythe", start_hub=None):
        self.goal = ""  # The goal is a declarative representation of the aim of the experiment.
                        # It is used where possible to automate experiment setup and some amount of validation.
        self.trial_class = trial_class
        self.exp_data = exp_data
        self.num_trials = num_trials
        self.trial_outputs = {}  # A dict with the independent variable as key
        self.independent = independent
        self.dependent = dependent
        self.hosts = hosts  # If there is a host list, assume it is for Magi on Deter for now
        self.file_output = file_output
        self.user = user
        self.experiment_file = experiment_file
        self.start_hub = start_hub  # If not None, specifies a path to a hub that will be started if needed on each host

    # Run the experiment. If several hosts are named, parcel out the trials and independent variables
    # to each one and call them up. If none are named, we are running all of this here (perhaps
    # as part of a multi-host solution).
    def run(self, run_data={}):
        if self.hosts is None or not self.hosts:
            return self.run_this_host(run_data)
        else:
            return self.scatter_gather(run_data)

    # For now, create a .aal file, assume this is running on a deter users host and call up the orchestrator.
    # I am just testing this with hard-wired experiments for the password simulator for now.
    def scatter_gather(self, run_data={}):
        # For a first pass, run one trial on each host and aggregate the results
        all_threads = []
        for host in self.hosts:
            print 'will create a .aal file implicating this host,', host
            # But for now use ssh
            t = self.RunProcess(self.user, host, self.experiment_file, run_data)
            t.start()
            all_threads.append(t)
        # Wait for them all to finis
        for t in all_threads:
            t.join()
        # Collate the results
        all_data = [t.result for t in all_threads]
        print '++ all data is', all_data
        return all_data

    class RunProcess(threading.Thread):  # thread class for managing processes on other hosts

        def __init__(self, user, host, run_file, run_data):
            threading.Thread.__init__(self)
            self.user = user
            self.host = host
            self.run_file = run_file
            self.run_data = run_data
            self.result = None

        def run(self):
            call = ["ssh", self.user+"@"+self.host, "python", self.run_file]
            try:
                process = subprocess.Popen(call, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            except BaseException as e:
                print 'unable to run python subprocess:', e
                return
            line = process.stdout.readline()
            self.result = None
            while line != "":
                if line.startswith("processed:"):
                    print '** getting data from', self.host, line
                    self.result = eval(line[line.find('processed:') + 10:])
                line = process.stdout.readline()
            print process.communicate()

    # Runs a set of trials for each value of the independent variable, keeping all other values constant,
    # and returning the set of trial outputs.
    # run_data may be a function of the independent variable or a constant.
    def run_this_host(self, run_data={}):
        # Make sure there is a hub if needed
        hub_thread = self.start_hub_if_needed()
        self.trial_outputs = {}
        # Build up trial data from experiment data and run data
        trial_data_for_all_values = self.exp_data.copy()
        for key in run_data:
            trial_data_for_all_values[key] = run_data[key]
        # Append different data for the independent variable in each iteration
        independent_vals = [None]
        # The representation for independent variables isn't fixed yet. For now, a two-element list with
        # the name of the variable and a range object.
        if self.independent is not None and isinstance(self.independent[1], Range):
            independent_vals = range(self.independent[1].min, self.independent[1].max, self.independent[1].step)
            print 'expanded range to', independent_vals
        elif self.independent is not None and isinstance(self.independent[1], (list, tuple)):  # allow a direct list
            independent_vals = self.independent[1]

        for independent_val in independent_vals:
            trial_data = trial_data_for_all_values.copy()
            if self.independent is not None:
                trial_data[self.independent[0]] = independent_val
            self.trial_outputs[independent_val] = []
            for trial_number in range(self.num_trials):
                print "Trial", trial_number, "with", None if self.independent is None else self.independent[0], "=", \
                    independent_val
                trial = self.trial_class(data=trial_data)
                trial.run()
                self.trial_outputs[independent_val].append(trial.output())
        # Kill the hub process if one was created
        if hub_thread is not None:
            hub_thread.stop_hub()
        return self.trial_outputs

    class HubThread(threading.Thread):  # thread class for managing a hub

        def __init__(self, process):
            threading.Thread.__init__(self)
            self.process = subprocess

        def run(self):
            line = self.process.stdout.readline()
            while line != "":
                print "hub:", line
                line = self.process.stdout.readline()

        def stop_hub(self):
            self.process.stdin.write("q\n")
            self.process.communicate()

    def start_hub_if_needed(self):
        if self.start_hub is not None:
            # Create a DASH agent and attempt to register to see if there is a hub
            agent = DASHAgent()
            agent.register()
            if not agent.connected:
                print "** Starting hub on current host with", self.start_hub
                try:
                    process = subprocess.Popen(["python", self.start_hub], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    line = process.stdout.readline()
                    while "if you wish" not in line:
                        print 'hub:', line
                        line = process.stdout.readline()
                    hub_thread = self.HubThread(process)
                    hub_thread.start()
                    return hub_thread
                except BaseException as e:
                    print 'unable to run process for hub:', e
        return None

    def process_results(self):  # After calling run(), use to process and return the results
        # If the results are a dictionary, assume the key is the independent variable and process the outcomes
        # for each one
        if self.trial_outputs and isinstance(self.trial_outputs, dict):
            result = dict()
            for key in self.trial_outputs:
                result[key] = process_list_results(self.trial_outputs[key])
            return result
        return process_list_results(self.trial_outputs)


def process_list_results(list_results):
    # If each result is a list, zip them and attempt simple statistics on them
    if list_results and all([isinstance(x, (list, tuple)) for x in list_results]):
        print 'iterating simple statistics on', list_results
        return [simple_statistics([trial[i] for trial in list_results])
                for i in xrange(len(list_results[0]))]
    elif list_results and all([isinstance(x, numbers.Number) for x in list_results]):
        return simple_statistics(list_results)
    else:
        return list_results


def simple_statistics(numlist):
    print 'running simple statistics on', numlist
    if all([isinstance(x, numbers.Number) for x in numlist]):
        return [numpy.mean(numlist), numpy.median(numlist), numpy.var(numlist)]

