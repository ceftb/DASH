import nurse01

# Set up a bunch of nurses to run 'at the same time' by running each for a small number of steps until done
# (dovetailing!)

# Each of n nurses is given a different list of k patients
num_nurses = 20
num_patients = 5
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

# Then disconnect
for nurse in nurses:
    nurse.disconnect()

