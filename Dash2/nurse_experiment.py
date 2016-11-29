from client import Client
import nurse01
from nurse_hub import Event

# Set up a bunch of nurses to run 'at the same time' by running each for a small number of steps until done
# (dovetailing!)

# To see the results, start a nurse_hub, run this file and then type 'q' at the nurse hub. The hub will print
# a list of actions, and the number of times an agent wrote to the wrong spreadsheet.


# Each of n nurses is given a different list of k patients
def trial(num_nurses=20, num_patients=5, num_computers=10, num_medications=10):
    # Clear out/initialize the data on the hub
    experiment_client = Client()
    experiment_client.register()
    experiment_client.sendAction("initWorld", (num_computers, num_medications))

    # Set up the agents
    nurses = [nurse01.Nurse(ident=n, patients=["_p_" + str(n) + "_" + str(p) for p in range(1, num_patients + 1)])
              for n in range(0, num_nurses)]
    finished_agents = set()
    for nurse in nurses:
        nurse.traceLoop = False

    # Run each nurse until it runs out of things to do. Stop when all nurses have finished.
    while len(nurses) > len(finished_agents):
        for nurse in nurses:
            if nurse not in finished_agents:
                final_action = nurse.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                if final_action is None:
                    finished_agents.add(nurse)

    for nurse in nurses:
        nurse.disconnect()

    trial_events = experiment_client.sendAction("showEvents")
    trial_misses = len([e for e in trial_events if e.patient != e.spreadsheet_loaded])
    return trial_misses, trial_events

# Finally close up the server.
# I'm having trouble with this. I think I'll try a new approach where I don't kill and re-start the
# server between trials, just call a method to clear out all the intermediate data.
# t.nurse_hub.listening = False

#data = [trial() for i in range(0,5)]
misses, events = trial(num_computers=1)

#time.sleep(1)   # let everything else that is printing stuff out settle down

# Print the events, with highlighting for the errors
for e in events:
    print "!!" if e.patient != e.spreadsheet_loaded else "", e
print misses, "misses out of", len(events)
# Find out which computers were used most heavily
computer_events = {}
computer_misses = {}
for e in events:
    if e.computer in computer_events:
        computer_events[e.computer].append(e)
    else:
        computer_events[e.computer] = [e]
    if e.patient != e.spreadsheet_loaded:
        if e.computer in computer_misses:
            computer_misses[e.computer].append(e)
        else:
            computer_misses[e.computer] = [e]
print 'computer, number of uses, number of misses'
for c in computer_events:
    print c, len(computer_events[c]), len(computer_misses[c]) if c in computer_misses else 0
