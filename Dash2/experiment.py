import subprocess
import threading
import numbers
import numpy
import time
from trial import Trial
from parameter import Range
from dash import DASHAgent

# An experiment consists of a varying condition and for each condition a number of trials.
# trial.py shows how the trials can be customized, and phish_experiment.py gives an example of the experiment harness.


class Experiment(object):
    def __init__(self, trial_class=Trial, independent=None, dependent=None, exp_data={}, num_trials=3,
                 file_output=None, hosts=None,
                 #experiment_file="/users/blythe/webdash/Dash2/pass_experiment.py",
                 dash_home="/users/blythe/webdash",
                 imports="",  # e.g. 'import pass_experiment',
                 callback="",
                 user="blythe", start_hub=None):
        self.goal = ""  # The goal is a declarative representation of the aim of the experiment.
                        # It is used where possible to automate experiment setup and some amount of validation.
        self.trial_class = trial_class
        self.exp_data = exp_data
        self.num_trials = num_trials
        self.trial_outputs = {}  # A dict with the independent variable as key
        # dependent may be a function of a trial or a member variable of the trial.
        self.independent = independent
        self.dependent = dependent
        self.hosts = hosts  # If there is a host list, assume it is for Magi on Deter for now
        self.dash_home = dash_home
        self.imports = imports
        self.callback = callback
        self.file_output = file_output
        self.user = user
        #self.experiment_file = experiment_file
        self.start_hub = start_hub  # If not None, specifies a path to a hub that will be started if needed on each host


    # Run the experiment. If several hosts are named, parcel out the trials and independent variables
    # to each one and call them up. If none are named, we are running all of this here (perhaps
    # as part of a multi-host solution).
    def run(self, run_data={}):
        if self.hosts is None or not self.hosts:
            return self.run_this_host(run_data)
        else:
            return self.scatter_gather(run_data)

    # For now, create ssh calls in subprocesses for the other hosts.
    # I am just testing this with hard-wired experiments for the password simulator for now.
    def scatter_gather(self, run_data={}):
        # For a second pass, split up the independent values among the hosts
        independent_vals = self.compute_independent_vals()
        all_threads = []
        i = 0  # index into independent_vals
        h = 0  # host index
        g = len(independent_vals) / len(self.hosts)
        rem = len(independent_vals) % len(self.hosts)
        # Need to iterate over packets of work, probably single independent variable values and reduced trials
        # for now, so we can dole these out as machines finish tasks and faster machines naturally do more work.
        for host in self.hosts:
            # Gets a segment of the independent values (currently this leaves hosts unused if there are more
            # hosts than values, need to fix by combining with number of trials).
            num_vals = g + 1 if h < rem else g
            vals = [independent_vals[j + i] for j in range(0, num_vals)]
            i += num_vals
            h += 1
            #time.sleep(1)  # so the printing routines don't overwrite each other
            print 'will create a .aal file usingq host,', host, 'with vals', vals
            #time.sleep(1)  # so the printing routines don't overwrite each other
            # But for now use ssh
            t = self.RunProcess(self, host, vals)
            t.start()
            all_threads.append(t)
        # Wait for them all to finish
        for t in all_threads:
            t.join()
        # Collate the results
        all_data = [t.result for t in all_threads]
        print '++ all data is', all_data
        return all_data

    class RunProcess(threading.Thread):  # thread class for managing processes on another host

        def __init__(self, experiment, host, vals):
            threading.Thread.__init__(self)
            self.experiment = experiment
            self.host = host
            self.print_all_lines = True
            self.result = None

        # I'm having trouble sending the arguments, so this creates a custom file for each host,
        # relies on it having the same file system, and attempts to execute it on the host
        def run(self):
            filename = self.experiment.dash_home + "/Magi/Exp/f-" + self.host
            call = ["ssh", self.experiment.user+"@"+self.host, "python", filename]
            print 'call is', call
            with open(filename, 'w') as f:
                # for now, args is the set of independent variables this host will work on. Needs to be cleaned up.
                f.write('import sys\nsys.path.insert(0, \'' + self.experiment.dash_home +
                        '/Dash2\')\nfrom parameter import Range\n' + self.experiment.imports + '\n' +
                        # The callback has to be a function that takes hosts and num_trials among other things
                        self.experiment.callback + '(num_trials=' + str(self.experiment.num_trials) +
                        ', exp_data=' + str(self.experiment.exp_data) +
                        ', independent=' + str(self.experiment.independent) +
                        ', dependent=\'' + str(self.experiment.dependent) + '\')\n')
            start = time.time()
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
                elif self.print_all_lines:
                    print self.host, 'prints', line
                line = process.stdout.readline()
            print self.host, 'took', time.time() - start
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
        independent_vals = self.compute_independent_vals()

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
                trial_dependent = self.dependent(trial) if callable(self.dependent) else getattr(trial, self.dependent)
                self.trial_outputs[independent_val].append(trial_dependent)
        # Kill the hub process if one was created
        if hub_thread is not None:
            hub_thread.stop_hub()
        return self.trial_outputs

    def compute_independent_vals(self):
        independent_vals = [None]
        # The representation for independent variables isn't fixed yet. For now, a two-element list with
        # the name of the variable and a range object.
        if self.independent is not None and isinstance(self.independent[1], Range):
            independent_vals = range(self.independent[1].min, self.independent[1].max, self.independent[1].step)
            print 'expanded range to', independent_vals
        elif self.independent is not None and isinstance(self.independent[1], (list, tuple)):  # allow a direct list
            independent_vals = self.independent[1]
        return independent_vals
        

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
    #print 'running simple statistics on', numlist
    if all([isinstance(x, numbers.Number) for x in numlist]):
        return [numpy.mean(numlist), numpy.median(numlist), numpy.var(numlist), len(numlist)]

