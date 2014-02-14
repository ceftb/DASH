% -*- Mode: Prolog -*-

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(loggedIn/0).

:-consult('agentGeneral').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment variables

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

numResources(2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% I use this as a goal to set on the command line so I can test the model repeatedly with one keystroke.
toplevel :- testAgent(Plan, 20), format('~w\n', [Plan]).

% Test a sequence of actions by mimicking the top-level agent - choosing an action, performing it and repeating.
testAgent([],0).  % Stop when fixed plan length is exceeded
testAgent([],_) :- format('could do nothing', []), do(doNothing).  % Stop with an empty plan when the agent could do nothing
% Otherwise find the first action, assume it succeeded, repeat.
testAgent([A|R],N) :- do(A), updateBeliefs(A,1), initialWorld(World), M is N - 1, testAgent(R,M).

% These are the possible goals and primitive actions of the agent.
subGoal(performFirstStep(P)).
subGoal(decidePerformRest(P)).
subGoal(createAccount(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
subGoal(ensureLoggedIn(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
subGoal(ensureLoggedOut(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
subGoal(logIn(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
subGoal(retrieveAccountInformation(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
%subGoal(retrievePassword(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.

primitiveAction(createUsername(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(createPassword(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(clickCreateAccountButton(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(rememberUsername(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(rememberPassword(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(enterUsername(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(enterPassword(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(clickLogInButton(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.
primitiveAction(logOut(Resource)) :- numResources(NumResources), 0 =< Resource, Resource < NumResources.

goal(doWork).
goalWeight(doWork, 1).

% If there is a roster, deliver meds.
%goalRequirements(doWork, [createAccount(0), ensureLoggedIn(0), createAccount(1), ensureLoggedIn(1), ensureLoggedOut(0), ensureLoggedOut(1)]).
goalRequirements(doWork, [createAccount(0), ensureLoggedIn(0), ensureLoggedOut(0), ensureLoggedIn(0), ensureLoggedOut(0)]).

%goalRequirements(doWork, Requirements) :- numResources(NumResources), Resource is random(NumResources), determineRequirements(Resource, Requirements).
%goalRequirements(doWork, [doNothing]).
%determineRequirements(Resource, ensureLoggedIn(Resource)) :-
%determineRequirements(Resource, Requirements) :- inCurrentWorld(loggedIn).

goalRequirements(performFirstStep([Action|Rest]), [Action]). %,decide(performFirstStep(Rest))]).
%  :- format('considering ~w in plan ~w\n',[Action,[Action|Rest]]).

% Deciding to perform a list of steps by deciding each step in turn.
goalRequirements(decidePerformRest([]), [doNothing]).
goalRequirements(decidePerformRest([H|R]),[decide(performFirstStep(R)),decidePerformRest(R)]).

% Agent must execute the logIn step if not currently logged in to satisfy goal ensureLoggedIn
goalRequirements(createAccount(Resource), [createUsername(Resource), createPassword(Resource), clickCreateAccountButton(Resource)]) :- not(inCurrentWorld(createdAccount(Resource))), !.
goalRequirements(createAccount(Resource), [doNothing]) :- inCurrentWorld(createdAccount(Resource)), !.

goalRequirements(ensureLoggedIn(Resource), [logIn(Resource)]) :- not(inCurrentWorld(loggedIn(Resource))), inCurrentWorld(createdAccount(Resource)), !.
goalRequirements(ensureLoggedIn(Resource), [doNothing]) :- inCurrentWorld(loggedIn(Resource)), inCurrentWorld(createdAccount(Resource)), !.

goalRequirements(ensureLoggedOut(Resource), [logOut(Resource)]) :- inCurrentWorld(loggedIn(Resource)), inCurrentWorld(createdAccount(Resource)), !.
goalRequirements(ensureLoggedOut(Resource), [doNothing]) :- not(inCurrentWorld(loggedIn(Resource))), inCurrentWorld(createdAccount(Resource)), !.

% To log in, the agent must retrieve their accountinformation and enter it.
goalRequirements(logIn(Resource), [retrieveAccountInformation(Resource), enterUsername(Resource), enterPassword(Resource), clickLogInButton(Resource)]).

% There may be many ways to retrieve a password. Here we expect to remember it. (other ideas-- read from post it note, read from text document on computer, ask spouse, call help desk, request password be sent to email address, guess?... the appropriate action could be based on beliefs)
goalRequirements(retrieveAccountInformation(Resource), [rememberUsername(Resource), rememberPassword(Resource)]).

% Update rules for primitive actions
% Changing beliefs based on reports about attempted actions

% Tell the agent the action was already performed in the initial state so that utility analysis will work.
updateBeliefs(createAccount(Resource), 1) :- addToWorld(performed(createAccount(Resource))), addToWorld(createdAccount(Resource)), !.
updateBeliefs(logIn(Resource), 1) :- addToWorld(performed(logIn(Resource))), addToWorld(loggedIn(Resource)), !.
updateBeliefs(logOut(Resource), 1) :- addToWorld(performed(logOut(Resource))), removeFromWorld(loggedIn(Resource)), !.

updateBeliefs(clickCreateAccountButton(Resource), 1) :- addToWorld(performed(clickCreateAccountButton(Resource))), addToWorld(createdAccount(Resource)), !.
updateBeliefs(clickLogInButton(Resource), 1) :- addToWorld(performed(clickLogInButton(Resource))), addToWorld(loggedIn(Resource)), !.
updateBeliefs(logOut(Resource), 1) :- addToWorld(performed(logOut(Resource))), removeFromWorld(loggedIn(Resource)), !.

updateBeliefs(Action,1) :- addToWorld(performed(Action)), !.

% Allow other facts that become true to be communicated from the model, so that changes in the world
% that are concurrent with the agent's actions can be noticed
updateBeliefs(Action,[]) :- addToWorld(performed(Action)), !.
updateBeliefs(Action,[H|R]) :- addToWorld(performed(Action)), addAuxiliaryFacts([H|R]).
updateBeliefs(_,_).

% Note Fact must be dynamic to be able to be asserted or retracted.

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).

removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)), retract(Fact).

% Begin with just an empty initial world. As we get the reports of actions
% we fill the world so that actions don't get repeated.
initialWorld([]).

reset :- assert(initialWorld([])).

% The set of mental models determines how the agent estimates the consequences of an action.
mentalModel([user]).

addSets(createAccount(Resource), user, World, [[1.0, createdAccount(Resource)]]).
addSets(ensureLoggedIn(Resource), user, World, [[1.0, loggedIn(Resource)]]).

% By default we simply add the fact that the action was performed. A default is needed for simulation
% to work and this setting is used in most of the cases.
addSets(Action,_,_,[[1.0, performed(Action)]]).

% Short-hand
performed(Action, World) :- member(performed(Action), World).

inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% I don't believe we're using the following currently
% but expansion of the model may make use of it.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%addAuxiliaryFacts([]).
%addAuxiliaryFacts([add(Fact)|R]) :- addToWorld(Fact), format('Added concurrent change ~w\n', [Fact]), addAuxiliaryFacts(R).
%addAuxiliaryFacts([del(Fact)|R]) :- removeFromWorld(Fact), addAuxiliaryFacts(R).

% 'decide(A)' is a built-in goal that performs action A if 'ok(A)' is true.

% If system 1 doesn't make a decision about whether an action is ok,
% use envisionment (projection) to see if we prefer the plan.
% WARNING: CURRENTLY ONLY WORKS WHEN THE ACTION IS THE FIRST STEP IN THE PLAN.
%system2Fact(ok(performFirstStep([Action|Rest]))) :-
%format('\ndeciding whether to ~w\n', [Action]),
%incr(envision), initialWorld(I), preferPlan([Action|Rest],Rest,I).

% We don't currently check which patient meds were delivered to, since
% the scenario only deals with one. Since the utility predicate doesn't
% test this we will need to maintain the current patient on focus as the
% goal tree builds up. We count the number of patients delivered too, so if a
% plan delivers/documents any patient it will get extra utility
%utility(W,U) :- bagof(P,rewarded(W,P),B), length(B,L), !, sumActionCost(W,Cost), U is 100 * L - Cost.
%utility(W,U) :- sumActionCost(W,Cost), U is 0 - Cost.

%sumActionCost([],0).
%sumActionCost([performed(A)|R],S) :- !, cost(A,C), sumActionCost(R,O), S is C + O.
%sumActionCost([H|R],S) :- sumActionCost(R,S).

% For now every action costs 5 units.
%cost(_,5).

% Similarly you must have a trigger to avoid a crash.
%trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.

% This means the agent chooses between alternate outcomes by which has the higher utility score.
% At the moment there is no alternative.
%decisionTheoretic.

% Copied from mailReader.pl
%incr(Fieldname) :- field(Fieldname,N), New is N + 1, retractall(field(Fieldname,_)), assert(field(Fieldname,New)).

%field(envision, 0).