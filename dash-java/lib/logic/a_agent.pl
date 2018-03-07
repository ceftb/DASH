% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
:-style_check(-singleton).
:-style_check(-discontiguous).
goalRequirements(plantOK,[try(pump, on), check(rupture)]) :- low(wp).
goalRequirements(try(V1,V2),[check(V1)]) :- value(V1,unknown).
goalRequirements(try(V1,V2),[doNothing]) :- value(V1,V2).
goalRequirements(try(V1,V2),[set(V1,V2)]).
goal(plantOK).
goalWeight(plantOK, 1).
primitiveAction(set(_,_)).
primitiveAction(doNothing).
primitiveAction(check(_)).
subGoal(try(_,_)).


updateBeliefs(set(V1,V2),1) :-  retractall(value(V1,_)), assert(value(V1,V2)).
updateBeliefs(check(V1),V) :-  retractall(value(V1,_)), assert(value(V1,V)).
% Generic update rule
updateBeliefs(_,_).
:-dynamic(low/1).
low(V1) :- [value(V1,V), acceptable(V1,L,H), V < L].
:-dynamic(value/2).
value(wp,50).
:-dynamic([value/2).
:-dynamic(acceptable/3).
acceptable(wp,40,80).
:-dynamic(</2).
id(1).
