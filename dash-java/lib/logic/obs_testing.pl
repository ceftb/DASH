:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(observations/1).

:- consult('agentGeneral').

goal(soleGoal).
goalWeight(soleGoal, 1).

primitiveAction(sleepAction(this, is, [a, test])).

goalRequirements(soleGoal, [sleepAction(this, is, [a, test])]).

updateBeliefs(_,_).
