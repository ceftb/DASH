% -*- Mode: Prolog -*-

% Agent to compare and modify a plan to deliver medications to
% patients. The original plan may be compliant with some (nominal)
% protocol, while the agent makes modifications according to its
% personal utility structure.

% Current status: considers dropping individual steps in sequence.
% Want to consider substituting steps, re-ordering steps, particularly in
% sequences of plans, (somehow) modifying steps to remove preconditions
% or effects and adding (some kind of) step to defeat bad things or add good things.

% In the current agent, the nurse skips scanning when p(document| no scan) >= 0.95

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).

:-consult('agentGeneral').

% I use this as a goal to set on the command line so I can test the model repeatedly with one keystroke.
toplevel :- testAgent(Plan, 7), format('~w\n', [Plan]).

% Test a sequence of actions by mimicking the top-level agent - choosing an action, performing it and repeating.
% BUG: DOESN'T SHOW THE LAST ACTION ALTHOUGH IT IS CONSIDERED IN THE COMPUTATION FOR ALL THE OTHER ACTIONS.
testAgent([],0).
testAgent([A|R],N) :- do(A), updateBeliefs(A,1), M is N - 1, testAgent(R,M).

goal(deliverMeds(_)).
goalWeight(deliverMeds(_), 1).

% For now this will just consider the utility of performing the first
% step. Will code later for all steps sequentially.
goalRequirements(deliverMeds(Patient), 
                 [decide(performFirstStep(Plan)),decidePerformRest(Plan)])
  :- onRoster(Patient), initialWorld(World), not(inWorld(deliver(_,Patient),World)), protocol(Patient,Plan), !.
goalRequirements(deliverMeds(_),[doNothing]).

goalRequirements(performFirstStep([Action|Rest]), [Action]). %,decide(performFirstStep(Rest))]).
%  :- format('considering ~w in plan ~w\n',[Action,[Action|Rest]]).

goalRequirements(decidePerformRest([]), [doNothing]).
goalRequirements(decidePerformRest([H|R]),[decide(performFirstStep(R)),decidePerformRest(R)]).

protocol(Patient, 
	[eMAR_Review(Patient),
	 retrieveMeds(Patient, Meds),
	 scan(Patient),
         scan(Meds),
         deliver(Meds, Patient),
         document(Meds, Patient)])
     :- requiredMeds(Patient, Meds).

% 'decide(A)' is a built-in goal that performs action A if 'ok(A)' is true.

% If system 1 doesn't make a decision about whether an action is ok,
% use envisionment (projection) to see if we prefer the plan.
% WARNING: CURRENTLY ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
system2Fact(ok(performFirstStep([Action|Rest]))) :- 
	incr(envision), initialWorld(I), preferPlan([Action|Rest],Rest,I).

% Begin with just an empty initial world. As we get the reports of actions
% we fill the world so that actions don't get repeated.
initialWorld([]).

reset :- assert(initialWorld([])).

subGoal(performFirstStep(P)).
subGoal(decidePerformRest(P)).
primitiveAction(eMAR_Review(P)).
primitiveAction(retrieveMeds(P,M)).
primitiveAction(scan(X)).
primitiveAction(deliver(M,P)).
primitiveAction(document(M,P)).


mentalModel([nurse]).   % nurse or official

% We need adds and deletes for each step in the plan and a utility model
% for final outcomes.

% You must currently have one addSets predicate defined to use
% projection or the program will crash.

% In the 'official' model, everything happens as per the manual.

% projecting through deliver() will have no effect if haveMeds() is not true
addSets(deliver(Meds,Patient),   official, World, 
                                 [[1.0, performed(deliver(Meds, Patient))]])
  :- inWorld(retrieveMeds(Patient,Meds), World), !.
addSets(deliver(Meds,Patient),   official, World, [[1.0]]) :- !.  % otherwise nothing happens

% In the 'official' model, must have scanned in the appropriate place etc. to document.
addSets(document(Meds, Patient), official, World, [[1.0, performed(document(Meds, Patient))]]) 
  :- inWorld(eMAR_Review(Patient), World),
     inWorld(scan(Patient), World),
     inWorld(scan(Meds), World), !.

% Otherwise, projection should not fail, or so will comparing the plans
addSets(document(Meds, Patient), official, World, [[1.0]]) :- !.


% Differences for the individual's model: documenting does not require the eMAR review (or scanning).
% The probability of successfully performing the task are higher with the scans, though.

addSets(document(Meds, Patient), nurse, World, [[1.0, performed(document(Meds, Patient))]]) 
  :- inWorld(scan(Patient), World),
     inWorld(scan(Meds), World), !.

addSets(document(Meds, Patient), nurse, World, [[0.95, performed(document(Meds, Patient))],[0.05]]).


% Otherwise, the nurse model performs like the official one
addSets(Action, nurse, World, Sets) :- addSets(Action, official, World, Sets), !.


% By default we simply add the fact that the action was performed. A default is needed for simulation
% to work and this setting is used in most of the cases.
addSets(Action,_,_,[[1.0, performed(Action)]]).

% We don't currently check which patient meds were delivered to, since
% the scenario only deals with one. Since the utility predicate doesn't
% test this we will need to maintain the current patient on focus as the
% goal tree builds up.
utility(W,U) :- inWorld(deliver(M,P),W), inWorld(document(M,P),W), !, sumActionCost(W,Cost), U is 100 - Cost.
utility(W,U) :- sumActionCost(W,Cost), U is 0 - Cost.

inWorld(Action, World) :- member(performed(Action), World).

sumActionCost([],0).
sumActionCost([performed(A)|R],S) :- !, cost(A,C), sumActionCost(R,O), S is C + O.
sumActionCost([H|R],S) :- sumActionCost(R,S).

% For now every action costs 5 units.
cost(_,5).

% Similarly you must have a trigger to avoid a crash.
trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.

% This means the agent chooses between alternate outcomes by which has the higher utility score.
% At the moment there is no alternative.
decisionTheoretic.


% Changing beliefs based on reports about attempted actions
%updateBeliefs(eMAR_Review(Patient), 1) :- addToWorld(eMAR_Reviewed(Patient)), !.
%updateBeliefs(retrieveMeds(Patient, Meds), 1) :- addToWorld(haveMeds(Patient, Meds)), !.
%updateBeliefs(scan(X), 1) :- addToWorld(scanned(X)), !.
% Tell the agent the action was already performed in the initial state so that utility analysis will work.
updateBeliefs(Action,1) :- addToWorld(performed(Action)), !.
updateBeliefs(_,_).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).

% Copied from mailReader.pl
incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

field(envision, 0).

% Initial goals
onRoster(joe).
requiredMeds(joe, [percocet]).
