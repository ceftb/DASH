% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
:-style_check(-singleton).
:-style_check(-discontiguous).
goalRequirements(top,[sm(M)]) :- ms(M).
goalRequirements(top,[doNothing]) :- not(ms(M)).
goalRequirements(sm(V1),[sendMessage(V1,T)]) :- privacyTool(T), installed(T).
goalRequirements(sm(V1),[install(T), sendMessage(V1,T)]) :- privacyTool(T), not(installed(T)).
goalRequirements(install(V1),[visitUrl(V1), downloadSoftware(V1)]).
primitiveAction(downloadSoftware(_)).
subGoal(install(_)).
subGoal(sm(_)).
primitiveAction(sendMessage(_,_)).
primitiveAction(doNothing).
goal(top).
goalWeight(top, 1).
primitiveAction(visitUrl(_)).


updateBeliefs(downloadSoftware(V1),1) :- assert(installed(V1)).
updateBeliefs(sendMessage(V1,V2),1) :-  retract(ms(V1)).
% Generic update rule
updateBeliefs(_,_).
:-dynamic(ms/1).
ms(hi).
ms(there).
:-dynamic(privacyTool/1).
privacyTool(tor).
:-dynamic(installed/1).
id(1).
