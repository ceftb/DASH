% -*- Mode: Prolog -*-

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(signedIn/0).
:- dynamic(requirementsSet/1).
:- dynamic(userInitialized/0).
:- consult('agentGeneral').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% basic resource stuff
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

numResources(2).

% the id's of the resources
resourceIDs([100, 101]).

resourceExists(Resource) :- numResources(NumResources), 0 =< Resource, Resource < NumResources, !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% iteration stuff
% ...for testing in isolation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% iterations of loop
run :- kIterations(50).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- format('\n\nchoosing action...\n'), system1, do(X), format('chose action ~w\n', X), updateBeliefs(X, 1), system1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal stuff
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% depth 0 goal
goal(doWork).
goalWeight(doWork, 1).

% depth 1 goals
subGoal(createAccount(Resource)) :- resourceExists(Resource).
subGoal(ensureSignedIn(Resource)) :- resourceExists(Resource).
subGoal(ensureSignedOut(Resource)) :- resourceExists(Resource).

% depth 2 goals
subGoal(attemptCreateAccount(Resource)) :- resourceExists(Resource).
subGoal(attemptSignIn(Resource)) :- resourceExists(Resource).
subGoal(attemptSignOut(Resource)) :- resourceExists(Resource).

% depth 3 goals
subGoal(retrieveAccountInformation(Resource)) :- resourceExists(Resource).

% only done once to initialize user state
executable(initializeUser).

% primitive actions and executables associated with creating account
executable(comeUpWithUsername(Resource)) :- resourceExists(Resource).
executable(comeUpWithPassword(Resource)) :- resourceExists(Resource).
primitiveAction(clickCreateAccountButton(Resource)) :- resourceExists(Resource).
primitiveAction(recognizeAccountCreated(Resource)) :- resourceExists(Resource).

% primitive actions and executables associated with signing in
executable(rememberUsername(Resource)) :- resourceExists(Resource).
executable(rememberPassword(Resource)) :- resourceExists(Resource).
primitiveAction(enterUsername(Resource)) :- resourceExists(Resource).
primitiveAction(enterPassword(Resource)) :- resourceExists(Resource).
primitiveAction(clickSignInButton(Resource)) :- resourceExists(Resource).
primitiveAction(recognizeSignedIn(Resource)) :- resourceExists(Resource).

% primitive actions and executables associated with signing out
primitiveAction(clickSignOutButton(Resource)) :- resourceExists(Resource).
primitiveAction(recognizeSignedOut(Resource)) :- resourceExists(Resource).


% goal requirements for various goals and subgoals
goalRequirements(doWork, Requirements) :- requirementsSet(Requirements), !.
goalRequirements(doWork, [initializeUser]) :- not(requirementsSet(X)), not(userInitialized), assert(userInitialized), !.
goalRequirements(doWork, Requirements) :- not(requirementsSet(X)), numResources(NumResources), Resource is random(NumResources), determineRequirements(Resource, Requirements), assert(requirementsSet(Requirements)), ansi_format([fg(blue)], 'new requirements set: ~w\n', [Requirements]), !.

determineRequirements(Resource, [createAccount(Resource)]) :- not(inCurrentWorld(createdAccount(Resource))), !.
determineRequirements(Resource, [ensureSignedIn(Resource)]) :- R is random(2), R is 0, !.
determineRequirements(Resource, [ensureSignedOut(Resource)]) :- !.

goalRequirements(createAccount(Resource), [attemptCreateAccount(Resource), recognizeAccountCreated(Resource)]) :- not(inCurrentWorld(createdAccount(Resource))), !.
goalRequirements(createAccount(Resource), [recognizeAccountCreated(Resource)]) :- inCurrentWorld(createdAccount(Resource)), !.

goalRequirements(attemptCreateAccount(Resource), [comeUpWithUsername(Resource), comeUpWithPassword(Resource), clickCreateAccountButton(Resource)]).

goalRequirements(ensureSignedIn(Resource), [attemptSignIn(Resource), recognizeSignedIn(Resource)]) :- inCurrentWorld(createdAccount(Resource)), not(inCurrentWorld(signedIn(Resource))), !.
goalRequirements(ensureSignedIn(Resource), [recognizeSignedIn(Resource)]) :- inCurrentWorld(createdAccount(Resource)), inCurrentWorld(signedIn(Resource)), !.

goalRequirements(ensureSignedOut(Resource), [clickSignOutButton(Resource), recognizeSignedOut(Resource)]) :- inCurrentWorld(createdAccount(Resource)), inCurrentWorld(signedIn(Resource)), !.
goalRequirements(ensureSignedOut(Resource), [recognizeSignedOut(Resource)]) :- inCurrentWorld(createdAccount(Resource)), not(inCurrentWorld(signedIn(Resource))), !.

% To sign in, the agent must retrieve their accountinformation and enter it.
goalRequirements(attemptSignIn(Resource), [retrieveAccountInformation(Resource), enterUsername(Resource), enterPassword(Resource), clickSignInButton(Resource)]).

% There may be many ways to retrieve a password. Here we expect to remember it. (other ideas-- read from post it note, read from text document on computer, ask spouse, call help desk, request password be sent to email address, guess?... the appropriate action could be based on beliefs)
goalRequirements(retrieveAccountInformation(Resource), [rememberUsername(Resource), rememberPassword(Resource)]).

% executes!
execute(initializeUser) :- format('executing ~w.\n', initializeUser).
execute(comeUpWithUsername(Resource)) :- format('executing ~w.\n', comeUpWithUsername(Resource)).
execute(comeUpWithPassword(Resource)) :- format('executing ~w.\n', comeUpWithUserPassword(Resource)).
execute(rememberUsername(Resource)) :- format('executing ~w.\n', rememberUsername(Resource)).
execute(rememberPassword(Resource)) :- format('executing ~w.\n', rememberPassword(Resource)).


% Update rules for primitive actions
% Changing beliefs based on reports about attempted actions

% Tell the agent the action was already performed in the initial state so that utility analysis will work.

updateBeliefs(clickCreateAccountButton(Resource), _) :- ansi_format([fg(red)], 'update beliefs called with clickCreateAccountButton\n', []), addToWorld(performed(clickCreateAccountButton(Resource))), addToWorld(createdAccount(Resource)), !.
updateBeliefs(clickSignInButton(Resource), _) :- ansi_format([fg(red)], 'update beliefs called with clickSignInButton\n', []), addToWorld(performed(clickSignInButton(Resource))), addToWorld(signedIn(Resource)), !.
updateBeliefs(clickSignOutButton(Resource), _) :- ansi_format([fg(red)], 'update beliefs called with clickSignOutButton\n', []), addToWorld(performed(clickSignOutButton(Resource))), removeFromWorld(signedIn(Resource)), !.

updateBeliefs(recognizeAccountCreated(Resource), _) :- addToWorld(performed(recognizeAccountCreated(Resource))), retract(requirementsSet(Requirements)), !.
updateBeliefs(recognizeSignedIn(Resource), _) :- addToWorld(performed(recognizeSignedIn(Resource))), retract(requirementsSet(Requirements)), !.
updateBeliefs(recognizeSignedOut(Resource), _) :- addToWorld(performed(recognizeSignedOut(Resource))), retract(requirementsSet(Requirements)), !.

updateBeliefs(Action, _) :- addToWorld(performed(Action)), !.

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

% The set of mental models determines how the agent estimates the consequences of an action.
mentalModel([user]).

% catch all addSets used for projection
addSets(Action, _, _, [[1.0, performed(Action)]]).

% Short-hand
performed(Action, World) :- member(performed(Action), World).

inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% regarding account creation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%generateUsernname(Resource) :- addToWorld(generatedUsername(Resource, )).
%generatePassword(Resource) :- firstName(F), lastName(L), addToWorld(generatedUsername().

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% account information retrieval
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% I don't believe we're using the following currently
% but expansion of the model may very well make use of it.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%subGoal(performFirstStep(P)).
%subGoal(decidePerformRest(P)).

%goalRequirements(performFirstStep([Action|Rest]), [Action]). %,decide(performFirstStep(Rest))]).
%  :- format('considering ~w in plan ~w\n',[Action,[Action|Rest]]).

%goalRequirements(decidePerformRest([]), [doNothing]).
%goalRequirements(decidePerformRest([H|R]),[decide(performFirstStep(R)),decidePerformRest(R)]).

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