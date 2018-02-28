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
:- dynamic(loggedIn/0).

:-consult('agentGeneral').

% I use this as a goal to set on the command line so I can test the model repeatedly with one keystroke.
toplevel :- testAgent(Plan, 20), format('~w\n', [Plan]).

% Test a sequence of actions by mimicking the top-level agent - choosing an action, performing it and repeating.
testAgent([],0).
testAgent([],_) :- do(doNothing).
testAgent([A|R],N) :- do(A), updateBeliefs(A,1), initialWorld(World), M is N - 1, testAgent(R,M).

goal(doWork).
goalWeight(doWork, 1).

% Create a goal to deliver meds to each patient on the agent's roster.
goalRequirements(doWork, DeliverMeds) :- roster(Roster), buildDeliveryList(Roster,DeliverMeds), format('delivery plan is ~w\n', [DeliverMeds]), !.
goalRequirements(doWork, [doNothing]).

buildDeliveryList([],[]).
buildDeliveryList([First|Rest],[deliverMeds(First)|RestDeliveries]) :- buildDeliveryList(Rest,RestDeliveries).

% Top level goal retrieves the protocol and decides which step to perform
goalRequirements(deliverMeds(Patient), 
                 [decide(performFirstStep(Plan)),decidePerformRest(Plan)])
  :- format('Requirements for ~w\n', [Patient]), initialWorld(World), not(performed(document(_,Patient),World)), protocol(Patient,Plan), !.
goalRequirements(deliverMeds(_),[doNothing]).

goalRequirements(performFirstStep([Action|Rest]), [Action]). %,decide(performFirstStep(Rest))]).
%  :- format('considering ~w in plan ~w\n',[Action,[Action|Rest]]).

goalRequirements(decidePerformRest([]), [doNothing]).
goalRequirements(decidePerformRest([H|R]),[decide(performFirstStep(R)),decidePerformRest(R)]).

goalRequirements(ensureLoggedIn, [doNothing]) :- inCurrentWorld(loggedIn), !.
goalRequirements(ensureLoggedIn, [logIn]) :- not(inCurrentWorld(loggedIn)), !.

protocol(Patient, 
	[eMAR_Review(Patient),
	 retrieveMeds(Patient, Meds),
	 scan(Patient),
         scan(Meds),
         deliver(Meds, Patient),
	 ensureLoggedIn,
         document(Meds, Patient)])
     :- requiredMeds(Patient, Meds).

% 'decide(A)' is a built-in goal that performs action A if 'ok(A)' is true.

% If system 1 doesn't make a decision about whether an action is ok,
% use envisionment (projection) to see if we prefer the plan.
% WARNING: CURRENTLY ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
system2Fact(ok(performFirstStep([Action|Rest]))) :- 
    format('\ndeciding whether to ~w\n', [Action]), 
    incr(envision), initialWorld(I), preferPlan([Action|Rest],Rest,I).

% Begin with just an empty initial world. As we get the reports of actions
% we fill the world so that actions don't get repeated.
initialWorld([]).

reset :- assert(initialWorld([])).

subGoal(deliverMeds(_)).
subGoal(performFirstStep(P)).
subGoal(decidePerformRest(P)).
subGoal(ensureLoggedIn).
primitiveAction(eMAR_Review(P)).
primitiveAction(retrieveMeds(P,M)).
primitiveAction(scan(X)).
primitiveAction(deliver(M,P)).
primitiveAction(document(M,P)).
primitiveAction(logIn).


mentalModel([nurse]).   % nurse or official

% We need adds and deletes for each step in the plan and a utility model
% for final outcomes.

% You must currently have one addSets predicate defined to use
% projection or the program will crash.

% In the 'official' model, everything happens as per the manual.

% projecting through deliver() will have no effect if retrieveMeds(Patient,Meds) was not performed
addSets(deliver(Meds,Patient),   official, World, 
                                 [[1.0, performed(deliver(Meds, Patient))]])
  :- performed(retrieveMeds(Patient,Meds), World), !.
addSets(deliver(Meds,Patient),   official, World, [[1.0]]) :- !.  % otherwise nothing happens

addSets(ensureLoggedIn, official, World, [[1.0, loggedIn]]).

% In the 'official' model, must have scanned in the appropriate place etc. to document.
addSets(document(Meds, Patient), official, World, [[1.0, performed(document(Meds, Patient))]]) 
  :- performed(eMAR_Review(Patient), World),
     performed(scan(Patient), World),
     performed(scan(Meds), World), 
     member(loggedIn, World),
     !.

% Otherwise, projection should not fail, or so will comparing the plans
addSets(document(Meds, Patient), official, World, [[1.0]]) :- !.


% Differences for the individual's model: documenting does not require the eMAR review (or scanning).
% The probability of successfully performing the task are higher with the scans, though.

addSets(document(Meds, Patient), nurse, World, [[1.0, performed(document(Meds, Patient))]]) 
  :- performed(scan(Patient), World),
     performed(scan(Meds), World), 
     member(loggedIn, World),
     !.

addSets(document(Meds, Patient), nurse, World, [[0.95, performed(document(Meds, Patient))],[0.05]])
  :- member(loggedIn, World).


% Otherwise, the nurse model performs like the official one
addSets(Action, nurse, World, Sets) :- addSets(Action, official, World, Sets), !.


% By default we simply add the fact that the action was performed. A default is needed for simulation
% to work and this setting is used in most of the cases.
addSets(Action,_,_,[[1.0, performed(Action)]]).

% We don't currently check which patient meds were delivered to, since
% the scenario only deals with one. Since the utility predicate doesn't
% test this we will need to maintain the current patient on focus as the
% goal tree builds up. We count the number of patients delivered too, so if a
% plan delivers/documents any patient it will get extra utility
utility(W,U) :- bagof(P,rewarded(W,P),B), length(B,L), !, sumActionCost(W,Cost), U is 100 * L - Cost.
utility(W,U) :- sumActionCost(W,Cost), U is 0 - Cost.

rewarded(W,P) :- performed(deliver(M,P),W), performed(document(M,P),W).

performed(Action, World) :- member(performed(Action), World).

inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

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
updateBeliefs(logIn,1) :- addToWorld(performed(logIn)), addToWorld(loggedIn), !.
updateBeliefs(Action,1) :- addToWorld(performed(Action)), !.
% Allow other facts that become true to be communicated from the model, so that changes in the world
% that are concurrent with the agent's actions can be noticed
updateBeliefs(Action,[]) :- addToWorld(performed(Action)), !.
updateBeliefs(Action,[H|R]) :- addToWorld(performed(Action)), addAuxiliaryFacts([H|R]).
updateBeliefs(_,_).

addAuxiliaryFacts([]).
addAuxiliaryFacts([add(Fact)|R]) :- addToWorld(Fact), format('Added concurrent change ~w\n', [Fact]), addAuxiliaryFacts(R).
addAuxiliaryFacts([del(Fact)|R]) :- removeFromWorld(Fact), addAuxiliaryFacts(R).

% Note Fact must be dynamic to be able to be asserted or retracted.

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).

removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)), retract(Fact).

% Copied from mailReader.pl
incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

field(envision, 0).

% Initial goals
roster([joe,brian]).

requiredMeds(joe, [percocet]).
requiredMeds(brian, [codeine]).

