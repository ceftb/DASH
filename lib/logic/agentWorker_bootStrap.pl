% -*- Mode: Prolog -*-
%:- style_check(-singleton).
%:- style_check(-discontiguous).

id(1).

myManager(100).
myIT(6).
machineName(1).

agentState(unexpectedness, 0.2).
agentState(tiredness, 0.3).

overWorkedThresh(0.8).

tasks(0).
finishedTasks(0).

% 1 in 5 times on average check the spreadsheet
% Note: this probability is checked on every substep,
% so a 0.2 means it will almost certainly check at least once
% and probably twice on each 
checkSpreadsheetChance(0.1).

browserApp(explorer).
appOpen(explorer).
appHasFocus(explorer).
spreadsheetApp(sp1).

evil(false).
okToWork(true).
website('http://www.zulu.isp').

taskMap(_,label1).

goal(doWork).
goalWeight(doWork, 5).
