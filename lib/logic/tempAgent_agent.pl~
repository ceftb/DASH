% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
:-style_check(-singleton).
:-style_check(-discontiguous).
goalRequirements(plantOK,[try(pump, on), check(pipeRupture)]) :- low(waterPressure).
goalRequirements(try(V1,V2),[check(V1)]) :- value(V1, unknown).
goalRequirements(try(V1,V2),[doNothing]) :- value(V1, V2).
goalRequirements(try(V1,V2),[set(V1,V2)]).
goalRequirements(plantOK,[doNothing]).
goal(plantOK).
goalWeight(plantOK, 1).
primitiveAction(set(_,_)).
primitiveAction(doNothing).
primitiveAction(check(_)).
subGoal(try(_,_)).


updateBeliefs(set(V1,V2),1) :-   retractall(value(V1,_)), assert(value(V1,V2)).
updateBeliefs(check(V1),Value) :-    retractall(value(V1,_)), assert(value(V1,Value)).
% Generic update rule
updateBeliefs(_,_).
:-dynamic(low/1).
low(V1) :- value(V1,V), acceptable(V1,Low,High), V < Low.
:-dynamic(value/2).
value(waterPressure,30).
:-dynamic(acceptable/3).
acceptable(waterPressure,45,125).
:-dynamic(</2).
id(1).
