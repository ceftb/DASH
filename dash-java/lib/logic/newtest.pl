% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
% (These dynamic declarations currently added by hand).
goalRequirements(top,[sm(M)]) :- ms(M).
goalRequirements(top,[doNothing]) :- not(ms(M)).
goalRequirements(sm(V1),[sendMessage(V1,T)]) :- privacyTool(T), installed(T).
goalRequirements(sm(V1),[install(T), sendMessage(V1,T)]) :- privacyTool(T), not(installed(T)).
goalRequirements(install(V1),[visitUrl(V1), downloadSoftware(V1)]).
goal(top).
goalWeight(top, 1).
primitiveAction(downloadSoftware(_)).
subGoal(install(_)).
subGoal(sm(_)).
primitiveAction(sendMessage(_,_)).
primitiveAction(doNothing).
primitiveAction(visitUrl(_)).

% Added by hand but matches the new agent
updateBeliefs(_,_).

%% Other parts added by hand (for now)

:-dynamic(ms/1).
ms('hello, world').

privacyTool(tor).

:-dynamic(installed/1).

id(1).
