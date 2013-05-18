% -*- Mode: Prolog -*-
% Agent file created automatically by the wizard.
:-style_check(-singleton).
:-style_check(-discontiguous).
goalRequirements(deliverMeds(Patient),[decide(performInPlan(A,[A|Rest]))]) :- onRoster(Patient), not(delivered(Patient)), protocol(Patient,[A|Rest]).
goalRequirements(performInPlan(Action,Plan),[Action]) :- format('considering ~w in plan ~w\n',[Action,Plan]).
primitiveAction(deliver(Meds,Patient)).
goal(deliverMeds(Patient)).
goalWeight(deliverMeds(Patient), 1).
primitiveAction(document(Meds,Patient)).
primitiveAction(retrieveMeds(Patient,Meds)).
primitiveAction(Action).
primitiveAction(eMar_Review(Patient)).
primitiveAction(decide(_)).
primitiveAction(scan(X)).
goal(performInPlan(Action,Plan)).
goalWeight(performInPlan(Action,Plan), 1).


% Generic update rule
updateBeliefs(_,_).
:-dynamic(onRoster/1).
onRoster(johnDoe).
:-dynamic(delivered/1).
:-dynamic(protocol/2).
protocol(a,1).
protocol(Patient,V2) :- requiredMeds(Patient,Meds), createProtocol(Patient,Meds,V2).
%protocol(Patient,V2) :- :-dynamic(format/7).
:-dynamic(requiredMeds/2).
:-dynamic(createProtocol/3).
id(1).
