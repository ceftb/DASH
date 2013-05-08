% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
goalRequirements(top,[sm(M)]) :- ms(M).
goalRequirements(top,[doNothing]) :- not(ms(M)).
goalRequirements(sm(V1),[sendMessage(M,T)]) :- privacyTool(T), installed(T).
goalRequirements(sm(V1),[install(T), sendMessage(V1,T)]) :- privacyTool(T), not(installed(T)).
goalRequirements(install(V1),[visitUrl(V1), downloadSoftware(V1)]).
goal(top).
goalWeight(top, 1).
primitiveAction(downloadSoftware(V1)).
subGoal(install(V1)).
subGoal(sm(V1)).
primitiveAction(sendMessage(V1,V2)).
primitiveAction(doNothing).
primitiveAction(visitUrl(V1)).

% Added by hand but matches the new agent
updateBeliefs(_,_).

%% Other parts added by hand (for now)

:-dynamic(installed/1).
:-dynamic(ms/1).
:-dynamic(privacyTool/1).
%privacyTool(tor).
ms(hi).
