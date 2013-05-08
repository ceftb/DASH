% -*- Mode: Prolog -*-

id(100).

checkPCChance(0).
delegateTaskChance(1.0).
remainingSubTasks(0).
taskFillSpreadsheet('Supp', 2, 2).
%taskFillSpreadsheet('Supp', 1, 1).
tasks(2).
%tasks(1).
error(5).
worker(1).
workers(1).
goal(doWork).
currentWorker(1).

goalWeight(doWork, 5).

