% -*- Mode: Prolog -*-

% Agent to compare and modify a plan to deliver medications to
% patients. The original plan may be compliant with some (nominal)
% protocol, while the agent makes modifications according to its
% personal utility structure.

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(delivered/1).
:- dynamic(field/2).

goal(deliverMeds(_)).
goalWeight(deliverMeds(_), 1).

% For now this will just consider the utility of performing the first
% step. Will code later for all steps sequentially.
goalRequirements(deliverMeds(Patient), [decide(performInPlan(A,[A|Rest]))])
  :- onRoster(Patient), not(delivered(Patient)), protocol(Patient,[A|Rest]).

goalRequirements(performInPlan(Action,Plan), [Action])
  :- format('considering ~w in plan ~w\n',[Action,Plan]).

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
% envision and see if we prefer the plan.
% WARNING: ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
system2Fact(ok(performInPlan(Action,[Action|Rest]))) :- 
	incr(envision), preferPlan([Action|Rest],Rest,[]).

subGoal(performInPlan(A,P)).
primitiveAction(eMAR_Review(P)).
primitiveAction(retrieveMeds(P,M)).
primitiveAction(scan(X)).
primitiveAction(deliver(M,P)).
primitiveAction(document(M,P)).


mentalModel([nurse]).

% We need adds and deletes for each step in the plan and a utility model
% for final outcomes.

% You must currently have one addSets predicate defined to use
% projection or the program will crash.

% In the 'official' model, everything happens as per the manual.

addSets(eMAR_Review(Patient), official, _,
	[[1.0, eMAR_Reviewed(Patient)]]).

addSets(retrieveMeds(Patient,Meds), official, _,
        [[1.0, haveMeds(Patient,Meds)]]).

addSets(scan(X), official, _, [[1.0, scanned(X)]]).

% projecting through deliver() will fail if haveMeds() is not true
addSets(deliver(Meds,Patient),   official, World, [[1.0, delivered(Meds, Patient)]])
  :- member(haveMeds(Patient,Meds), World).

% In the 'official' model, must have scanned in the appropriate place etc. to document.
addSets(document(Meds, Patient), official, World, [[1.0, documented(Meds, Patient)]]) 
  :- member(eMAR_Reviewed(Patient), World),
     member(scanned(Patient), World),
     member(scanned(Meds), World), !.
% Otherwise, projection should not fail, or so will comparing the plans
addSets(document(Meds, Patient), official, World, [[1.0]]).


% Differences for the individual's model: documenting does not require the eMAR review (or scanning).
% Leaving scanning in for now because I want to alter the probabilities of the different outcomes for that.

addSets(document(Meds, Patient), nurse, World, [[1.0, documented(Meds, Patient)]]) 
  :- member(scanned(Patient), World),
     member(scanned(Meds), World), !.

% Otherwise, the nurse model performs like the official one
addSets(Action, nurse, World, Sets) :- addSets(Action, official, World, Sets).


% We don't currently check which patient meds were delivered to, since
% the scenario only deals with one. Since the utility predicate doesn't
% test this we will need to maintain the current patient on focus as the
% goal tree builds up.
utility(W,U) :- member(delivered(M,P),W), member(documented(M,P),W), !, sumActionCost(W,Cost), U is 100 - Cost.
utility(W,U) :- sumActionCost(W,Cost), U is 0 - Cost.

sumActionCost([],0).
sumActionCost([performed(A)|R],S) :- !, cost(A,C), sumActionCost(R,O), S is C + O.
sumActionCost([H|R],S) :- sumActionCost(R,S).

% For now every action costs 5 units.
cost(_,5).

% Similarly you must have a trigger to avoid a crash.
trigger(World, _, [World], 0).  % by default, nothing happens

% This means the agent chooses between alternate outcomes by which has the higher utility score.
% At the moment there is no alternative.
decisionTheoretic.


% Copied from mailReader.pl
incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

field(envision, 0).

onRoster(joe).
requiredMeds(joe, [percocet]).
