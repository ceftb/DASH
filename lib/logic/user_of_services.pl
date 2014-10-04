:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(signedIn/3).
:- dynamic(requirementsSet/1).
:- dynamic(userInitialized/0).
:- dynamic(createAccountResult/4).
:- dynamic(signInResult/4).
:- dynamic(signOutResult/4).
:- dynamic(createdAccount/1).

:- dynamic(desiredUsername/2).
:- dynamic(desiredPassword/2).
:- dynamic(latestResult/2).

% this is asserted during updateBeliefs for the intializeUser primitiveAction
:- dynamic(services/1).
:- dynamic(count/1).

:- consult('agentGeneral').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% iteration stuff
% ...for testing in isolation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% iterations of loop
run :- kIterations(50).
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- format('\n\nchoosing action...\n'), system1, do(X), format('chose action ~w\n', X), updateBeliefs(X, 1), system1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% high level, general, and utility content %%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% high level and general goal content %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% top level goal
goal(doWork).
goalWeight(doWork, 1).

% high level subgoals that can be thought of tasks the agent is working on
subGoal(createAccount(Service)) :- serviceExists(Service).
subGoal(signIn(Service)) :- serviceExists(Service).
subGoal(signOut(Service)) :- serviceExists(Service).

% goal requirements for various goals and subgoals
goalRequirements(doWork, Requirements) :- sleep(1), requirementsSet(Requirements), !.
goalRequirements(doWork, [initializeUser]) :- not(requirementsSet(X)), not(userInitialized), ansi_format([fg(blue)], 'initializing user.\n', []), !.
goalRequirements(doWork, Requirements) :- not(requirementsSet(X)), chooseService(Service), determineRequirements(Service, Requirements), assert(requirementsSet(Requirements)), ansi_format([fg(blue)], 'new requirements set: ~w\n', [Requirements]), !.

determineRequirements(Service, [createAccount(Service)]) :- not(inCurrentWorld(createdAccount(Service))), !.
determineRequirements(Service, [signIn(Service)]) :- R is random(2), R is 0, !.
determineRequirements(Service, [signOut(Service)]) :- !.

% the primitiveAction initializeUser is the very first action the agent performs.
% the purpose is to synchronize the hub with the user
% as a response, the hub returns the list of services available to the user.
% this list of users is then asserted in updateBeliefs
% perhaps, later, we can instead have this result contain more information (e.g., other users)
primitiveAction(initializeUser).
updateBeliefs(initializeUser, R) :- ansi_format([fg(red)], 'update beliefs called with initializeUser. result: ~w\n', [R]), addToWorld(performed(initializeUser)), assert(R), assert(userInitialized), !.

% this is used to reset the current task the user is working on
% it is executed as the last step to achieving a particular task
executable(resetRequirements).
execute(resetRequirements) :- retractall(requirementsSet(_)), format('executing ~w.\n', resetRequirements).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% general and utility content %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% check whether a service exists
serviceExists(Service) :- services(ServiceList), member(Service, ServiceList).

% choose a service at random
chooseService(Service) :- services(ServiceList), length(ServiceList, Length), ServiceIndex is random(Length), nth0(ServiceIndex, ServiceList, Service).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% tracking changed to world %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% begin with an empty initial world
initialWorld([]).

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

% check if a fact exists in the world
inCurrentWorld(Fact) :- initialWorld(World), member(Fact, World).

% check if an action is performed in the world
performed(Action, World) :- member(performed(Action), World).

%%%%%%%%%%%%%%%%%%%%
% planning content %
%%%%%%%%%%%%%%%%%%%%

% The set of mental models determines how the agent estimates the consequences of an action.
mentalModel([user]).

% catch all addSets used for projection
addSets(Action, _, _, [[1.0, performed(Action)]]).

%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%% createAccount %%%%
%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%

% remarks:
% - perhaps consider numerous methods for username/password construction... for example, correct-horse-battery-staple method
% - expand on memory model for memorizing and recalling passwords

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

subGoal(attemptCreateAccount(Service)).
subGoal(enterDesiredUsernameSG(Service)).
executable(chooseUsername(Service)).
primitiveAction(enterDesiredUsername(Service, Username)) :- inCurrentWorld(desiredUsername(Service, Username)).
subGoal(enterDesiredPasswordSG(Service)).
executable(choosePassword(Service)).
primitiveAction(enterDesiredPassword(Service, Password)) :- inCurrentWorld(desiredPassword(Service, Password)).
primitiveAction(clickCreateAccountButton(Service, Username, Password)) :- inCurrentWorld(desiredUsername(Service, Username)), inCurrentWorld(desiredPassword(Service, Password)).
subGoal(setupForAccountRetrieval(Service)).
executable(memorizeUsername(Service)).
executable(memorizePassword(Service)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goalRequirements(createAccount(Service), [attemptCreateAccount(Service), setupForAccountRetrieval(Service), resetRequirements]).

goalRequirements(attemptCreateAccount(Service), [enterDesiredUsernameSG(Service), enterDesiredPasswordSG(Service), clickCreateAccountButton(Service, Username, Password)]).

goalRequirements(enterDesiredUsernameSG(Service), [chooseUsername(Service), enterDesiredUsername(Service, Username)]).
goalRequirements(enterDesiredPasswordSG(Service), [choosePassword(Service), enterDesiredPassword(Service, Password)]).

goalRequirements(setupForAccountRetrieval(Service), [memorizeUsername(Service), memorizePassword(Service)]).

repeatable(attemptCreateAccount(Service)) :- not(inCurrentWorld(createdAccount(Service))).
repeatable(enterDesiredUsernameSG(Service)) :- inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), reject(tooShort))); inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), reject(alreadyTaken))).
repeatable(enterDesiredPasswordSG(Service)) :- inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), reject(tooShort))); inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), accept(weak))).

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_un)), format('executing ~w - branch 1.\n', chooseUsername(Service)).
execute(chooseUsername(Service)) :- inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), reject(tooShort))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_longer_username)), format('executing ~w - branch 2.\n', chooseUsername(Service)), !.
execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [reject(tooShort), _])), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, test_longer_username)), format('executing ~w - branch 3.\n', chooseUsername(Service)), !.
execute(chooseUsername(Service)) :- inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), reject(alreadyTaken))), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, hopefully_this_is_not_taken)), format('executing ~w - branch 4.\n', chooseUsername(Service)), !.
execute(chooseUsername(Service)) :- not(inCurrentWorld(latestResult(enterDesiredUsername(Service, Username), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [reject(alreadyTaken), _])), removeFromWorld(desiredUsername(Service, _)), addToWorld(desiredUsername(Service, hopefully_this_is_not_taken)), format('executing ~w - branch 5.\n', chooseUsername(Service)), !.

execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, test_pw)), format('executing ~w - branch 1.\n', choosePassword(Service)).
execute(choosePassword(Service)) :- inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), reject(tooShort))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1)), format('executing ~w - branch 2.\n', choosePassword(Service)).
execute(choosePassword(Service)) :- inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), accept(weak))), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1234)), format('executing ~w - branch 3.\n', choosePassword(Service)).
execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [_, reject(tooShort)])), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1)), format('executing ~w - branch 4.\n', choosePassword(Service)).
execute(choosePassword(Service)) :- not(inCurrentWorld(latestResult(enterDesiredPassword(Service, Password), Result))), inCurrentWorld(latestResult(createAccount(Service, Username, Password), [_, accept(weak)])), removeFromWorld(desiredPassword(Service, _)), addToWorld(desiredPassword(Service, password1234)), format('executing ~w - branch 5.\n', choosePassword(Service)).

% usernamedUsedForAccount and passwordUsedForAccount are temporarily used to store the username and password
% for agent recall, we must used something else that is set up here...
% right now, the basic model I am just using has form usernameBeliefs(Service, [(username1, strength1), (username2, strength2),...]
% the idea is that whenever a username is used correctly, belief in that username is set to 1 while the others are set to 0
% however, every agent "step" for which it is not used, the strengths of usernames used for the service is spread over all usernames
% used over all services. The rate of spread could also be a factor of how many times the username was remembered correctly for the service
% ... so, for example, if you use a username once, you're likely to forget it; if you use it 100 times, you'll be more likely to remember it in the future
% and the rate at which you forget it will decline.

execute(memorizeUsername(Service)) :- inCurrentWorld(usernameUsedForAccount(Service, Username)), removeFromWorld(usernameUsedForAccount(Service, Username)), addToWorld(usernameBeliefs(Service, [[Username, 1]])), format('executing ~w.\n', [memorizeUsername(Service)]).
execute(memorizePassword(Service)) :- inCurrentWorld(passwordUsedForAccount(Service, Password)), removeFromWorld(passwordUsedForAccount(Service, Password)), addToWorld(passwordBeliefs(Service, [[Password, 1]])), format('executing ~w.\n', [memorizePassword(Service)]).

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefs(enterDesiredUsername(Service, Username), Result) :- removeFromWorld(latestResult(enterDesiredUsername(Service, _), _)), addToWorld(latestResult(enterDesiredUsername(Service, Username), Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [enterDesiredUsername(Service, Username), Result]).

updateBeliefs(enterDesiredPassword(Service, Password), Result) :- removeFromWorld(latestResult(enterDesiredPassword(Service, _), _)), addToWorld(latestResult(enterDesiredPassword(Service, Password), Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [enterDesiredPassword(Service, Password), Result]).

updateBeliefs(clickCreateAccountButton(Service, Username, Password), accept) :- removeFromWorld(latestResult(clickCreateAccountButton(Service, _, _), _)), removeFromWorld(latestResult(enterDesiredUsername(Service, _), _)), removeFromWorld(latestResult(enterDesiredPassword(Service, _), _)), addToWorld(createdAccount(Service)), addToWorld(usernameUsedForAccount(Service, Username)), addToWorld(passwordUsedForAccount(Service, Password)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickCreateAccountButton(Service, Username, Password), accept]).
updateBeliefs(clickCreateAccountButton(Service, Username, Password), Result) :- Result \= accept, removeFromWorld(latestResult(clickCreateAccountButton(Service, _, _), _)), removeFromWorld(latestResult(enterDesiredUsername(Service, _), _)), removeFromWorld(latestResult(enterDesiredPassword(Service, _), _)), addToWorld(latestResult(createAccount(Service, Username, Password), Result)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickCreateAccountButton(Service, Password), Result]).

%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%
%%%% signIn %%%%
%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

%%%%%%%% later...
%%%%%%%% we want subgoal: retrieveAccountInformation
%%%%%%%% which can be achieved by goal reqs like...
%%%%%%%%    recallUsername(Service), recallPassword(Service)
%%%%%%%%    readUsernameFromPostIt(Service), readPasswordFromPostIt(Service)
%%%%%%%%    findFileContainingAccountInformation(Service), readUsernameFromFile(Service), readPasswordFromFile(service)

% subgoals, primitive actions, and executables associated with signing in
subGoal(attemptSignIn(Service)).
subGoal(retrieveAndEnterAccountInformation(Service)).
primitiveAction(recallAndEnterUsername(Service, Username)) :- recallUsername(Service, Username), !.
primitiveAction(recallAndEnterPassword(Service, Password)) :- recallPassword(Service, Password), !.
primitiveAction(clickSignInButton(Service, Username, Password)) :- inCurrentWorld(recalledUsername(Service, Username)), inCurrentWorld(recalledPassword(Service, Password)), !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% signIn goal requirements

goalRequirements(signIn(Service), [attemptSignIn(Service), resetRequirements]) :- format('expanding goal reqs for sign in - cp1.\n'), inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), format('expanding goal reqs for sign in - cp2.\n'), !.
goalRequirements(signIn(Service), [resetRequirements]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.

repeatable(attemptSignIn(Service)) :- sleep(1), not(inCurrentWorld(signedIn(Service, _, _))), !.

% To sign in, the agent must retrieve their accountinformation and enter it.
goalRequirements(attemptSignIn(Service), [retrieveAndEnterAccountInformation(Service), clickSignInButton(Service, Username, Password)]).

goalRequirements(retrieveAndEnterAccountInformation(Service), [recallAndEnterUsername(Service, Username), recallAndEnterPassword(Service, Password)]).

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

% there are none right now!

%%%%%%%%%%%%
% utility  %
%%%%%%%%%%%%

recallUsername(Service, Username) :- inCurrentWorld(recalledUsername(Service, Username)), !.
recallUsername(Service, Username) :- not(inCurrentWorld(recalledUsername(Service, Username))), usernameBeliefs(Service, List), maxList(List, Username), addToWorld(recalledUsername(Service, Username)), !.

recallPassword(Service, Password) :- inCurrentWorld(recalledPassword(Service, Password)), !.
recallPassword(Service, Password) :- not(inCurrentWorld(recalledPassword(Service, Password))), passwordBeliefs(Service, List), maxList(List, Password), addToWorld(recalledPassword(Service, Password)), !.

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefs(clickSignInButton(Service, Username, Password), accept) :- addToWorld(signedIn(Service, Username, Password)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickSignInButton(Service, Username, Password), accept]).

updateBeliefs(clickSignInButton(Service, Username, Password), reject(Result)) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignInButton(Service, Username, Password), reject(Result)]).

%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%
%%%% signOut %%%%
%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

subGoal(attemptSignOut(Service)).
primitiveAction(clickSignOutButton(Service, Username)) :- inCurrentWorld(signedIn(Service, Username, _)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

goalRequirements(signOut(Service), [attemptSignOut(Service), resetRequirements]) :- inCurrentWorld(createdAccount(Service)), inCurrentWorld(signedIn(Service, _, _)), !.
goalRequirements(signOut(Service), [resetRequirements]) :- inCurrentWorld(createdAccount(Service)), not(inCurrentWorld(signedIn(Service, _, _))), !.

goalRequirements(attemptSignOut(Service), [clickSignOutButton(Service, Username)]).


%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

% no executes!

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

updateBeliefs(clickSignOutButton(Service, Username), accept) :- removeFromWorld(signedIn(Service, Username, _)), ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w\n', [clickSignOutButton(Service, Username), accept]).

updateBeliefs(clickSignOutButton(Service, Username), reject(Result)) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w... this case still needs to be implemented!\n', [clickSignOutButton(Service, Username), reject(Result)]).

%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%
%%%% template %%%%
%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% subgoals, primitive actions, and executables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% goal requirements and repeatables %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%
% executes %
%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%
% updateBeliefs %
%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% more utility content, which must be placed at the end of this file %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% the default updateBeliefs if nothing is specified
updateBeliefs(Action, Result) :- ansi_format([fg(red)], 'update beliefs called with ~w. result: ~w (default call)\n', [Action, Result]), !.

%%%%%%%
% fin %
%%%%%%%

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
