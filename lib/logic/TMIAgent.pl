% -*- Mode: Prolog -*-

% Simple agent to model responses to sensor data in two ways. Using
% system 2, analyzes all the data it believes and picks the diagnoses
% consistent with the data and chooses an action indicated by
% them. 

% Using system 1, picks the diagnosis consistent with the most amount
% of data on a first-pass check and picks the action consistent with
% that.

% If running outside of the Detergent framework, need to load agentGeneral.pl first.

:- style_check(-singleton).
:- style_check(-discontiguous).

goalRequirements(doWork, [diagnoseAndRespond]).

goalRequirements(diagnoseAndRespond, [Action])
  :- diagnose(Problem), appropriateAction(Problem, Action).


diagnose(lossOfCoolant)
  :- pressure(internal, P), P < 30, temperature(internal, T), T > 75.

diagnose(lossOfCoolant)
  :- pressure(internal, P), P > 50, temperature(internal, T), T >= 100.

diagnose(overPressurization)
  :- pressure(internal, P), P > 50, not(diagnose(lossOfCoolant)).

appropriateAction(lossOfCoolant,open(hpi)).
appropriateAction(overPressurization,close(hpi)).


% In system 1, the rule 'if A then B at X' should probably be read as
% 'spreading activation goes from A to B with factor X'.

if pressure(internal, P) and less(P, 30) then lossOfCoolant at 1.
if pressure(internal, P) and greater(P, 50) then overPressurization at 1.

if lossOfCoolant then important(pressure(internal)) at 1.
if lossOfCoolant then important(temperature(internal)) at 1.
if lossOfCoolant then important(open(porv)) at 1.

if overPressurization then important(pressure(internal)) at 1.
if overPressurization then important(open(hpi)) at 1.
if overPressurization and open(hpi) then chooseAction(close(hpi)) at 1.

% Current beliefs (should come via system 1)

pressure(internal, 60).
temperature(something, 100).
open(solenoid(porv)).
open(hpi).

% For now get system1 facts from facts here
system1Fact(pressure(X,Y),1) :- pressure(X,Y).
system1Fact(temperature(X,Y),1) :- temperature(X,Y).
system1Fact(open(X),1) :- open(X).

id(1).
goal(doWork).
goalWeight(doWork,1).

subGoal(diagnoseAndRespond).

primitiveAction(open(hpi)).
primitiveAction(close(hpi)).

