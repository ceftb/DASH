:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(signedIn/0).
:- dynamic(requirementsSet/1).
:- dynamic(userInitialized/0).
:- dynamic(createAccountResult/4).
:- dynamic(signInResult/4).
:- dynamic(signOutResult/4).

% this is asserted during updateBeliefs for the intializeUser primitiveAction
:- dynamic(services/1).

:- consult('agentGeneral').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% basic service stuff
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% the services and their ids
% services([100]).

serviceExists(Service) :- services(ServiceList), member(Service, ServiceList).

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

% primary goals
goal(doWork).
goalWeight(doWork, 1).

% high level subgoals
subGoal(createAccount(Service)) :- serviceExists(Service).
subGoal(ensureSignedIn(Service)) :- serviceExists(Service).
subGoal(ensureSignedOut(Service)) :- serviceExists(Service).

% this is only done once to create the user
% the purpose is to synchronize the hub with the user
% additionally, any state the user has should be initialized here
primitiveAction(initializeUser).

% subgoals, primitive actions, and executables associated with creating account
subGoal(attemptCreateAccount(Service)) :- serviceExists(Service).
executable(comeUpWithUsername(Service)) :- serviceExists(Service).
executable(comeUpWithPassword(Service)) :- serviceExists(Service).
primitiveAction(enterDesiredUsername(Service)) :- serviceExists(Service).
primitiveAction(enterDesiredPassword(Service)) :- serviceExists(Service).
subGoal(clickCreateAccountButton(Service)) :- serviceExists(Service).

primitiveAction(recognizeAccountCreated(Service)) :- serviceExists(Service).

% subgoals, primitive actions, and executables associated with signing in
subGoal(attemptSignIn(Service)) :- serviceExists(Service).
subGoal(retrieveAccountInformation(Service)) :- serviceExists(Service).
executable(rememberUsername(Service)) :- serviceExists(Service).
executable(rememberPassword(Service)) :- serviceExists(Service).
primitiveAction(enterUsername(Service)) :- serviceExists(Service).
primitiveAction(enterPassword(Service)) :- serviceExists(Service).
subGoal(clickSignInButton(Service)) :- serviceExists(Service).

primitiveAction(recognizeSignedIn(Service)) :- serviceExists(Service).

% subgoals, primitive actions, and executables associated with signing out
subGoal(attemptSignOut(Service)) :- serviceExists(Service).
subGoal(clickSignOutButton(Service)) :- serviceExists(Service).

primitiveAction(recognizeSignedOut(Service)) :- serviceExists(Service).

% goal requirements for various goals and subgoals
goalRequirements(doWork, Requirements) :- requirementsSet(Requirements), !.
goalRequirements(doWork, [initializeUser]) :- not(requirementsSet(X)), not(userInitialized), !.
goalRequirements(doWork, Requirements) :- not(requirementsSet(X)), chooseService(Service), determineRequirements(Service, Requirements), assert(requirementsSet(Requirements)), ansi_format([fg(blue)], 'new requirements set: ~w\n', [Requirements]), !.

determineRequirements(Service, [createAccount(Service)]) :- not(inCurrentWorld(createdAccount(Service))), !.
determineRequirements(Service, [ensureSignedIn(Service)]) :- R is random(2), R is 0, !.
determineRequirements(Service, [ensureSignedOut(Service)]) :- !.

chooseService(Service) :- services(ServiceList), length(ServiceList, Length), ServiceIndex is random(Length), nth0(ServiceIndex, ServiceList, Service).


% createAccount goal requirements

goalRequirements(createAccount(Service), [attemptCreateAccount(Service), recognizeAccountCreated(Service)]).
repeatable(attemptCreateAccount(Service)) :- sleep(1), not(createAccountResult(Service, _, _, success)), !.


goalRequirements(attemptCreateAccount(Service), [comeUpWithUsername(Service), enterDesiredUsername(Service), comeUpWithPassword(Service), enterDesiredPassword(Service), clickCreateAccountButton(Service)]).

goalRequirements(clickCreateAccountButton(Service), [callPerson(Service, createAccount(MyID, test_username, test_password))])
:- id(MyID).

% ensureSignedIn goal requirements

goalRequirements(ensureSignedIn(Service), [attemptSignIn(Service), recognizeSignedIn(Service)]) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service))), !.
goalRequirements(ensureSignedIn(Service), [recognizeSignedIn(Service)]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service)), !.
repeatable(attemptSignIn(Service)) :- sleep(1), not(signInResult(Service, _, _, success)), not(signInResult(Service, _, _, alreadySignedIn)), !.

% To sign in, the agent must retrieve their accountinformation and enter it.
goalRequirements(attemptSignIn(Service), [retrieveAccountInformation(Service), enterUsername(Service), enterPassword(Service), clickSignInButton(Service)]).

goalRequirements(clickSignInButton(Service), [callPerson(Service, signIn(MyID, test_username, test_password))])
:- id(MyID).

% There may be many ways to retrieve a password. Here we expect to remember it. (other ideas-- read from post it note, read from text document on computer, ask spouse, call help desk, request password be sent to email address, guess?... the appropriate action could be based on beliefs)
goalRequirements(retrieveAccountInformation(Service), [rememberUsername(Service), rememberPassword(Service)]).

goalRequirements(ensureSignedOut(Service), [attemptSignOut(Service), recognizeSignedOut(Service)]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service)), !.
goalRequirements(ensureSignedOut(Service), [recognizeSignedOut(Service)]) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service))), !.

goalRequirements(attemptSignOut(Service), [clickSignOutButton(Service)]).
repeatable(attemptSignOut(Service)) :- sleep(1), not(signOutResult(Service, _, _, success)), !.

goalRequirements(clickSignOutButton(Service), [callPerson(Service, signOut(MyID, test_username, test_password))])
:- id(MyID).

% executes!
execute(comeUpWithUsername(Service)) :- format('executing ~w.\n', comeUpWithUsername(Service)).
execute(comeUpWithPassword(Service)) :- format('executing ~w.\n', comeUpWithPassword(Service)).
execute(rememberUsername(Service)) :- format('executing ~w.\n', rememberUsername(Service)).
execute(rememberPassword(Service)) :- format('executing ~w.\n', rememberPassword(Service)).


% Update rules for primitive actions
% Changing beliefs based on reports about attempted actions

% Tell the agent the action was already performed in the initial state so that utility analysis will work.

updateBeliefs(recognizeAccountCreated(Service), _) :- ansi_format([fg(red)], 'update beliefs called with recognizeAccountCreated(~w)\n', [Service]), addToWorld(performed(recognizeAccountCreated(Service))), retract(requirementsSet(Requirements)), addToWorld(createdAccount(Service)), retractall(createAccountResult(Service, _, _, _)), !.
updateBeliefs(recognizeSignedIn(Service), _) :- ansi_format([fg(red)], 'update beliefs called with recognizeSignedIn(~w)\n', [Service]), addToWorld(performed(recognizeSignedIn(Service))), retract(requirementsSet(Requirements)), addToWorld(signedIn(Service)), retractall(signInResult(Service, _, _, _)), !.
updateBeliefs(recognizeSignedOut(Service), _) :- ansi_format([fg(red)], 'update beliefs called with recognizeSignedOut(~w)\n', [Service]), addToWorld(performed(recognizeSignedOut(Service))), retract(requirementsSet(Requirements)), removeFromWorld(signedIn(Service)), retractall(signOutResult(Service, _, _, _)), !.

% the result of updateBeliefs for the user is just the services that are provided to the user
% we simply assert this result so the user is aware of what services are available
% perhaps, later, we can instead have this result contain more information
% such as the users within the system.
updateBeliefs(initializeUser, R) :- ansi_format([fg(red)], 'update beliefs called with initializeUser. result: ~w\n', [R]), addToWorld(performed(initializeUser)), assert(R), assert(userInitialized), !.

updateBeliefs(recognizeSignedOut(Service), _) :- !.

updateBeliefs(Action, _) :- addToWorld(performed(Action)), !.

% Allow other facts that become true to be communicated from the model, so that changes in the world
% that are concurrent with the agent's actions can be noticed
updateBeliefs(Action,[]) :- addToWorld(performed(Action)), !.
updateBeliefs(Action,[H|R]) :- addToWorld(performed(Action)), addAuxiliaryFacts([H|R]).
updateBeliefs(_,_).

% Note Fact must be dynamic to be able to be asserted or retracted.

% add Fact to world if it is not already part of the world
addToWorld(Fact) :- initialWorld(I), member(Fact, I), !.
addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).

% remove Fact from world (once) if it is already part of the world
removeFromWorld(Fact) :- initialWorld(I), not(member(Fact, I)), !.
removeFromWorld(Fact) :- initialWorld(I), member(Fact, I), select(Fact, I, J), retract(initialWorld(I)), assert(initialWorld(J)), !.

% we could have also used the following but it allows for duplicate facts
% -- this may not cause errors but seems semantically incorrect and may lead to errors down the road
% addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).
% removeFromWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), delete(I,Fact,J), assert(initialWorld(J)), retract(Fact).

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

%generateUsernname(Service) :- addToWorld(generatedUsername(Service, )).
%generatePassword(Service) :- firstName(F), lastName(L), addToWorld(generatedUsername().

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
