% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
:-style_check(-singleton).
:-style_check(-discontiguous).
goalRequirements(plantOk,[doNothing]) :- ok(waterPressure).
goalRequirements(plantOk,[fixLowPressure(waterPressure)]) :- low(waterPressure).
goalRequirements(fixLowPressure(V1),[try(feedwaterPump, V1, on), check(pipeRupture), try(bypassValve, V1, closed), try(emergencySealantSpray, V1, on)]).
goalRequirements(try(V1,V2,V3),[check(V2)]) :- value(V1,V3).
goalRequirements(try(V1,V2,V3),[check(V1), try2(V1,V2,V3)]) :- relevant(V1), value(V1, unknown).
goalRequirements(try(V1,V2,V3),[doNothing]) :- not(relevant(V1)).
goalRequirements(try2(V1,V2,V3),[set(V1,V3), check(V2)]).
primitiveAction(set(_,_)).
primitiveAction(doNothing).
subGoal(fixLowPressure(_)).
primitiveAction(check(_)).
subGoal(try(_,_,_)).
subGoal(try2(_,_,_)).
goal(plantOk).
goalWeight(plantOk, 1).


updateBeliefs(set(V1,V2),1) :-  retractall(value(V1,_)), assert(value(V1,V2)).
updateBeliefs(check(V1),ue) :-  retractall(value(V1,_)), assert(value(V1,Value)).
% Generic update rule
updateBeliefs(_,_).
:-dynamic(ok/1).
:-dynamic(low/1).
:-dynamic(value/2).
value(waterPressure,-2).
value(feedwaterPump,unknown).
value(bypassValve,unknown).
value(emergencySealantSpray,unknown).
:-dynamic(relevant/1).
relevant(feedwaterPump).
:-dynamic(retractall/1).
id(1).
