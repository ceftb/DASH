import threading
import time
from client import Client
import nurse01
import nurse_hub
from nurse_hub import Event

# Set up a bunch of nurses to run 'at the same time' by running each for a small number of steps until done
# (dovetailing!)

# To see the results, start a nurse_hub, run this file and then type 'q' at the nurse hub. The hub will print
# a list of actions, and the number of times an agent wrote to the wrong spreadsheet.


# Run a nurse hub in a separate thread
class NurseThread(threading.Thread):
    def run(self):
        self.nurse_hub = nurse_hub.NurseHub()
        self.nurse_hub.run()

#t = NurseThread()
#t.start()


# Each of n nurses is given a different list of k patients
def trial(num_nurses=20, num_patients=5):
    nurses = [nurse01.Nurse(["_p_" + str(n) + "_" + str(p) for p in range(1, num_patients + 1)])
              for n in range(0, num_nurses)]
    finished_agents = set()

    # Run each nurse until it runs out of things to do. Stop when all nurses have finished.
    while len(nurses) > len(finished_agents):
        for nurse in nurses:
            if nurse not in finished_agents:
                final_action = nurse.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                if final_action is None:
                    finished_agents.add(nurse)
    # Then disconnect. Actually this seems to cause a problem so let's try not disconnecting
    #for nurse in nurses:
    #   nurse.disconnect()

    # Then read stuff out from the nurse thread.
    #t.nurse_hub.print_events()
    experiment_client = Client()
    experiment_client.register()
    events = experiment_client.sendAction("showEvents")
    misses = len([e for e in events if e.patient != e.spreadsheet_loaded])
    print misses, "entries on the wrong spreadsheet out of", len(events)

    # Finally clear out the data on the hub
    experiment_client.sendAction("initWorld", [10, 10])
    return misses

# Finally close up the server.
# I'm having trouble with this. I think I'll try a new approach where I don't kill and re-start the
# server between trials, just call a method to clear out all the intermediate data.
# t.nurse_hub.listening = False

data = [trial() for i in range(0,5)]

time.sleep(1)   # let everything else that is printing stuff out settle down

print 'miss data', data
