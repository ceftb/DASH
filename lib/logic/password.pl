%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(passwordsWritten/1).
:- dynamic(isLoggedInto/2).
:- dynamic(userData/2).
:- dynamic(passwordCreated/3).
:- dynamic(field/2).
:- dynamic(worldState/1).
:- dynamic(frustration/2).
:- dynamic(time/1).
:- dynamic(completionTime/2).
:- dynamic(passwordsWritten/1).
:- consult('agentGeneral').
:- consult('vk_aux').


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% sample execution using swipl:

% swipl -s password.pl
% createEnvironment(3, 3).
% kIterations(100).
% halt.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% general

% This simulation is broken up into time steps.
% During each time step, we iterate through the users and run a user iteration
% The primary steps involved in a user iteration are setting the user,
% choosing an action, updating the world based on this action,
% and updating the frustration experienced by the user.
% We also print out the passwords written and the average peak frustration
% over all users.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

oneIteration :- time(Time), runUserIterations(0), updateWorld, incrementTime(1), passwordsWritten(PasswordsWritten), ansi_format([fg(blue)], 'A total of ~w passwords have been written down thus far.\n', [PasswordsWritten]), !.


runUserIterations(User) :- numUsers(K), User < K, runUserIteration(User), NextUser is User + 1, runUserIterations(NextUser), !.
runUserIterations(User) :- numUsers(K), User = K.

runUserIteration(User) :- setUser(User), format('set user.\n'), time(Time), completionTime(User, CompletionTime), Time is CompletionTime + 1, updateBeliefs, system1, format('choosing action.\n'), chooseAction(Action), actionTime(Action, ActionTime), incrementCompletionTime(User, ActionTime), completionTime(User, NewCompletionTime), format('User ~w: performed action ~w with result 1 starting at time ~w. Will complete action at time ~w.\n', [User, Action, Time, NewCompletionTime]), format('updating state of world.\n'), actionUpdate(Action), format('adding action to world.\n'), addToWorld(Action), recordAction(User, Action), updateFrustration(User, Action), updatePeakFrustration(User), !.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time =< CompletionTime, latestAction(User, Action), format('User ~w: Still in process of carrying out last action: ~w .\n', [User, Action]), updateFrustration(User, Action), updatePeakFrustration(User), !.
runUserIteration(User) :- setUser(User), setLatestAction(User, NoAction), time(Time), completionTime(User, CompletionTime), Time >= CompletionTime, format('User ~w: I am doing nothing!\n', User), modifyFrustration(User, -0.25), updatePeakFrustration(User), !.

setUser(User)
:- retractall(runningUser(_)), assert(runningUser(User)).

updatePeakFrustration(User) :- peakFrustration(User, X), frustration(User, Y), Y > X, !, retract(peakFrustration(User, X)), assert(peakFrustration(User, Y)).
updatePeakFrustration(User).

updateWorld :- printAveragePeakFrustration.

printAveragePeakFrustration :- computeNetPeakFrustration(0, NetFrustration), numUsers(NumUsers), AverageFrustration is NetFrustration / NumUsers, ansi_format([fg(blue)], 'AveragePeakFrustration is ~w.\n', [AverageFrustration]).

computeNetPeakFrustration(User, Net) :- numUsers(K), User < K, NextUser is User + 1, peakFrustration(User, Frustration), computeNetPeakFrustration(NextUser, NextNet), Net is NextNet + Frustration.
computeNetPeakFrustration(User, 0) :- numUsers(K), User = K.

% update world state based on the action a user chooses.
actionUpdate(createPassword(User, Resource)) :- !, passwordRequirements(Resource, PasswordRequirements), createPassword(User, PasswordRequirements, Password), assert(passwordCreated(User, Resource, Password)).
actionUpdate(logIn(User, Resource)) :- !, retractall(isLoggedInto(User, Resource)), assert(isLoggedInto(User, Resource)).
actionUpdate(logOut(User, Resource)) :- !, retractall(isLoggedInto(User, Resource)).
actionUpdate(idle(User)).

actionUpdate(Action) :- format('could not update world with action because action ~w was not recognized.\n', Action).

addToWorld(Action)
:- worldState(Current), retract(worldState(Current)), addToEnd(Current, performed(Action), NewWorld), assert(worldState(NewWorld)).

%%%% regarding timing

time(0).                        % initial time is 0

incrementTime(Amount)
:- time(Time), NewTime is Time + Amount, retract(time(X)), assert(time(NewTime)).

incrementCompletionTime(User, IncrementTime)
:- completionTime(User, CompletionTime), NewCompletionTime is CompletionTime + IncrementTime, retract(completionTime(User, X)), assert(completionTime(User, NewCompletionTime)).

% duration of time it takes to carry out various actions
actionTime(createPassword(User, Resource), ActionTime) :- ActionTime is 4.
actionTime(logIn(User, Resource), ActionTime) :- ActionTime is 2.
actionTime(logOut(User, Resource), ActionTime) :- ActionTime is 2.

actionTime(idle(User), ActionTime) :- ActionTime is 3.

%%%% regarding frustration

updateFrustration(User, Action)
:- actionFrustration(Action, ActionFrustration), !, modifyFrustration(User, ActionFrustration).

% frustration associated with a given action during a single time step.
actionFrustration(createPassword(User, Resource), 4).
actionFrustration(logIn(User, Resource), 2).
actionFrustration(logOut(User, Resource), 1).
actionFrustration(idle(User), -10).

modifyFrustration(User, X) :- frustration(User, Y), Z is X + Y, Z < 0, !, retract(frustration(User, Y)), assert(frustration(User, 0)), format('changed frustration for user ~w from ~w to 0.\n', [User, Y, 0]).
modifyFrustration(User, X) :- frustration(User, Y), Z is X + Y, !, retract(frustration(User, Y)), assert(frustration(User, Z)), format('changed frustration for user ~w from ~w to ~w.\n', [User, Y, Z]).

recordAction(User, Action)
:- retractall(latestAction(User, Actions)), assert(latestAction(User, Action)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment variables
initialFrustrationRange(0, 100).
initialMemory(0, 10).
frustrationThresholdRange(100, 200).
memoryCapacityRange(20, 30).
probabilityWorkaroundKnowledge(1).

% creates K users, L COWs, and does other initialization tasks
createEnvironment(K, L)
:- createUsers(K),
assert(numUsers(K)),
createResources(L),
assert(numResources(L)),
assert(passwordsWritten(0)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% users

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

createUsers(K)
:- K > 1, KMinusOne is K - 1, createUser(KMinusOne), createUsers(KMinusOne).

createUsers(1)
:- createUser(0).

createUser(User)
:- assert(user(User)),
initFrustration(User),
initPeakFrustration(User),
initFrustrationThreshold(User),
initCompletionTime(User),
initUserData(User),            % this data is used in the construction of passwords
initMemoryUsage(User),         % how much user is currently remembering
initMemoryCapacity(User).      % how much the user is able to remember... when password memory usage exceeds capacity, users write down passwords

initFrustration(User) :- initialFrustrationRange(Min, Max), chooseInRange(Min, Max, Frustration), assert(frustration(User, Frustration)).

initPeakFrustration(User) :- frustration(User, Frustration), assert(peakFrustration(User, Frustration)).

initCompletionTime(User) :- assert(completionTime(User, -1)).

initFrustrationThreshold(User) :- frustrationThresholdRange(Min, Max), chooseInRange(Min, Max, Threshold), assert(frustrationThreshold(User, Threshold)).

% users use this information to construct their passwords
initUserData(User)
:- random_member(FirstName, [abraham, anne, bob, cathy, dorothy, fred, enoch, juan, melvin, william]),
random_member(LastName, [brown, goldstein, lee, patel, smith]),
random_member(Color, [red, blue, yellow, green, orange, violet, black, white]),
random_member(Pet, [cat, dog, goldfish, turtle]),
chooseInRange(1950, 2010, Year),
assert(userData(User, [FirstName, LastName, Color, Pet, Year])).

initMemoryUsage(User) :- initialMemory(Min, Max), chooseInRange(Min, Max, MemoryUsage), assert(memoryUsage(User, MemoryUsage)).

initMemoryCapacity(User) :- memoryCapacityRange(Min, Max), chooseInRange(Min, Max, Capacity), assert(memoryCapacity(User, Capacity)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% resources

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

createResources(K)
:- K > 1, KMinusOne is K - 1, createResource(KMinusOne), createResources(KMinusOne).

createResources(1)
:- createResource(0).

createResource(Resource)
:- assert(resource(Resource)),
initPasswordRequirements(Resource).

initPasswordRequirements(Resource)
:- random_member(MinLength, [4, 6, 8, 10, 12, 14, 16]),
random_member(MinDigits, [0, 1, 2]),
assert(passwordRequirements(Resource, [MinLength, MinDigits])).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% regarding passwords

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

updateMemoryUsage(User, Increment)
:- retract(memoryUsage(User, X)), Y is X + Increment, assert(memoryUsage(User, Y)), updatePasswordsWritten(User, Y).

updatePasswordsWritten(User, Usage)
:- memoryCapacity(User, Capacity), Usage > Capacity, !, retract(passwordsWritten(X)), Y is X + 1, assert(passwordsWritten(Y)).
updatePasswordsWritten(User, Usage).

createPassword(User, PasswordRequirements, Password)
:- passwordCreated(User, Resource, Password),
satisfiesConstraints(PasswordRequirements, Password),
updateMemoryUsage(User, 1).


createPassword(User, PasswordRequirements, pass)
:- satisfiesConstraints(PasswordRequirements, pass),
updateMemoryUsage(User, 2).

createPassword(User, PasswordRequirements, password1)
:- satisfiesConstraints(PasswordRequirements, password1),
updateMemoryUsage(User, 4).

createPassword(User, PasswordRequirements, Password)
:- userData(User, L),
I is random(2),
J is 1 - I,
nth0(I, L, First),
nth0(J, L, Second),
nth0(4, L, Third),
string_concat(First, Second, FirstSecond),
string_concat(FirstSecond, Third, Password),
satisfiesConstraints(PasswordRequirements, Password),
updateMemoryUsage(User, 8).

createPassword(User, PasswordRequirements, Password)
:- userData(User, L),
I is random(2),
J is 1 - I,
nth0(I, L, First),
nth0(J, L, Second),
nth0(2, L, Third),
nth0(3, L, Fourth),
nth0(4, L, Fifth),
string_concat(First, Second, FirstSecond),
string_concat(FirstSecond, Third, FirstToThird),
string_concat(FirstToThird, Fourth, FirstToFourth),
string_concat(FirstToFourth, Fifth, Password),
satisfiesConstraints(PasswordRequirements, Password),
updateMemoryUsage(User, 16).

satisfiesConstraints([MinLength, MinDigits], Password)
:- atom_chars(Password, PasswordList),
length(PasswordList, Length),
Length >= MinLength,
calculateNumDigits(PasswordList, NumDigits),
NumDigits >= MinDigits.

calculateNumDigits([H | T], NumDigits)
:- member(H, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
calculateNumDigits(T, X),
NumDigits is X + 1.

calculateNumDigits([H | T], NumDigits)
:- not(member(H, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])),
calculateNumDigits(T, NumDigits).

calculateNumDigits([], 0).

% recallPassword(User, Resource)
%   implementing something like this could be used to guess old passwords for a resource

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% goals

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% achieved goals may be repeated
repeatable(doSomething).
repeatable(logIn(User, Resource)).

% always do something-- only implemented goal.
goal(doSomething).
goalWeight(doSomething, 1).

% primitive actions... may want to expand some to subgoals such as leaveRoom
primitiveAction(idle(User)).
primitiveAction(createPassword(User, Resource)).
primitiveAction(logIn(User, Resource)).
primitiveAction(logOut(User, Resource)).

goalRequirements(doSomething, [Action])
:- runningUser(User), numResources(NumResources), Resource is random(NumResources), determineRequirement(User, Resource, Action).


determineRequirement(User, Resource, idle(User))
:- I is random(2), I is 0.

determineRequirement(User, Resource, createPassword(User, Resource))
:- not(passwordCreated(User, Resource, Password)).

determineRequirement(User, Resource, logIn(User, Resource))
:- passwordCreated(User, Resource, Password), not(isLoggedInto(User, Resource)).

determineRequirement(User, Resource, logOut(User, Resource))
:- passwordCreated(User, Resource, Password), isLoggedInto(User, Resource).

addSets(Action, _, _, [[1.0, performed(Action)]]).

% mental model of a user
mentalModel([user]).

% choose action that yields maximum utility
decisionTheoretic.

% world is initially empty
worldState([]).

% copied/pasted from bcma.pl
% Similarly you must have a trigger to avoid a crash.
trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.

inWorld(Action, World) :- member(performed(Action), World).