% -*- Mode: Prolog -*-

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% IMPORTANT additions that need to be made:

% - allow for actions to be interruptible
% - make time continuous (can give actions non-integer durations and invoke global actions at any time-- e.g. power outage-- that leads agents to reasses actions... this would work in conjunction with interruptibly of actions)
% - add more depth to users via attributes

% Workaround Prediction in a Medical Setting

% brief usage notes:
% - initially call createEnvironment(K, L) to create K users and L COWs
% - call kIterations(K) to run K time steps of the simulation. Each user either chooses an action, continues to perform an action chosen in a previous time step, or idles. kIterations(K) calls oneIteration k times. oneIteration calls runUserIteration for each user.

% sample execution:
%  createEnvironment(K, L).
%  kIterations(50).

% need to do:
% - add user attributes-- should these be randomized or set by user running simulation?
% - measure net exposure-- this should be trivial...

% end goals / brain storming

% user attributes
% anger temperament, anger reactionary, locus of control,
% perceived costs and benefits for self and organization, etc.

% measure net exposure
% knowledge of workaround is acquired by seeing others employ it
% likelihood of employing workaround is affected by the number of other users who employ it
% scout's good/bad user idea... related: "good" users may log out other users. bad users may not.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(worldState/1).
:- dynamic(frustration/2).
:- dynamic(time/1).
:- dynamic(sCupUsed/1).
:- dynamic(isLoggedInto/2).
:- dynamic(isInteractingWith/2).
:- dynamic(inactivityDuration/2).
:- dynamic(completionTime/2).
:- dynamic(knowledge/2).
:- dynamic(netExposure/1).
:- dynamic(sCupPlaced/1).
:- dynamic(sCupWorkaroundKnowledge/1).
:- consult('agentGeneral').
:- consult('vk_aux').

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% general

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%% multiple iterations
kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
kIterations(1) :- oneIteration.

%%%% one iteration corresponding to a single time unit... loop over all users
oneIteration :- time(Time), runUserIterations(0), updateWorld, incrementTime(1), netExposure(NetExposure), ansi_format([fg(blue)], 'Net Exposure so far is ~w.\n', [NetExposure]), !.

%%%% run iteration for each user
runUserIterations(User) :- numUsers(K), User < K, runUserIteration(User), NextUser is User + 1, runUserIterations(NextUser), !.
runUserIterations(User) :- numUsers(K), User = K.

%%%% a particular user iteration - note... the retraction of isInteractingWith(User, COW) is important!
%%%% we decrement frustration of each user by 1 on each time step... should do something else.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time is CompletionTime + 1, retractall(isInteractingWith(User, COW)), format('updating beliefs.\n'), updateBeliefs, format('engaging system1.\n'), system1, format('choosing action.\n'), chooseAction(Action), updateFrustration(User, Action), actionTime(Action, ActionTime), incrementCompletionTime(User, ActionTime), completionTime(User, NewCompletionTime), format('User ~w: performed action ~w with result 1 starting at time ~w. Will complete action at time ~w.\n', [User, Action, Time, NewCompletionTime]), format('updating state of world.\n'), actionUpdate(Action), format('adding action to world.\n'), addToWorld(Action), modifyFrustration(User, -0.25), updatePeakFrustration(User), !.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time =< CompletionTime, format('User ~w: Still in process of carrying out last action.\n', User), modifyFrustration(User, -0.25), updatePeakFrustration(User), !.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time >= CompletionTime, format('User ~w: Idling.\n', User), modifyFrustration(User, -0.25), updatePeakFrustration(User), !.

%%%% set current user
setUser(User)
:- retractall(runningUser(_)), assert(runningUser(User)).

%%%% update peak frustration
updatePeakFrustration(User) :- peakFrustration(User, X), frustration(User, Y), Y > X, !, retract(peakFrustration(User, X)), assert(peakFrustration(User, Y)).
updatePeakFrustration(User).

%%%% updateWorld
updateWorld :- updateCOWs(0), printAveragePeakFrustration.

%%%% print average peak frustration
printAveragePeakFrustration :- computeNetPeakFrustration(0, NetFrustration), numUsers(NumUsers), AverageFrustration is NetFrustration / NumUsers, ansi_format([fg(blue)], 'AveragePeakFrustration is ~w.\n', [AverageFrustration]).

computeNetPeakFrustration(User, Net) :- numUsers(K), User < K, NextUser is User + 1, peakFrustration(User, Frustration), computeNetPeakFrustration(NextUser, NextNet), Net is NextNet + Frustration.
computeNetPeakFrustration(User, 0) :- numUsers(K), User = K.

%%%% call updateCOW for each COW.
updateCOWs(COW) :- numCOWs(K), COW < K, updateCOW(COW), NextCOW is COW + 1, updateCOWs(NextCOW), !.
updateCOWs(COW) :- numCOWs(K), COW = K.

%%%% update the COW
% if no user is logged into COW, do nothing.
% if a user is interacting with a COW, we also need to do nothing.
% else, increment inactivity duration for that cow.
updateCOW(COW) :- not(isLoggedInto(User, COW)), !.
updateCOW(COW) :- isInteractingWith(User, COW), !.
updateCOW(COW) :- not(sCupPlaced(COW)), isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), NewTime is Timeout, retract(isLoggedInto(User, COW)), retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)), ansi_format([fg(green)], 'Timeout has occurred on COW ~w. Logging out user ~w from ~w.\n', [COW, User, COW]), ansi_format([fg(blue)], 'Incremented net exposure on COW ~w.\n', [COW]), !.
updateCOW(COW) :- sCupPlaced(COW), isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), NewTime is Timeout, retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)), ansi_format([fg(blue)], 'Incremented net exposure for COW ~w.\n', [COW]), !.
updateCOW(COW) :- isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), not(NewTime is Timeout), retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, NewTime)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)), ansi_format([fg(blue)], 'Incremented net exposure for COW ~w.\n', [COW]), !.
updateCOW(COW) :- format('Trying to update COW ~w: we should not be here.\n', COW).

%%%% update world based on the action.
actionUpdate(logIntoCOW(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(useCOWAfterLogIn(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterMove(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterLeave(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterMoveSCup(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterLeaveSCup(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(moveCOW(User, COW)). % retracting & interacting with is done automatically

% if user does not know about the workaround, then he/she learns about it with a probability of numberComprisedCOWs / numberCOWs
actionUpdate(leaveCOWUnattended(User, COW)) :- not(sCupWorkaroundKnowledge(User)), findall(X, sCupPlaced(X), Y), length(Y, NumSCupsPlaced), numCOWs(NumCOWs), R is random(NumCOWs), R < NumSCupsPlaced, assert(sCupWorkaroundKnowledge(User)). % retracting & interacting with is done automatically

actionUpdate(leaveCOWUnattended(User, COW)).
actionUpdate(logOut(User, COW)) :- retractall(isLoggedInto(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(placeSCup(User, COW)) :- retractall(inactivityDuration(COW, Time)), assert(isInteractingWith(User, COW)), assert(inactivityDuration(COW, 0)), assert(sCupPlaced(COW)).

actionUpdate(takeBreak(User)).

actionUpdate(Action) :- format('could not update world with action because action ~w was not recognized.\n', Action).

%%%% add action to world
addToWorld(Action)
:- worldState(Current), retract(worldState(Current)), addToEnd(Current, performed(Action), NewWorld), assert(worldState(NewWorld)).

addToEnd([H|R], Item, [H|NewList])
:- addToEnd(R, Item, NewList).

addToEnd([], Item, [Item]).

%%%% things regarding timing

time(0).                        % initial time is 0
netExposure(0).                 % net exposure (total time units that a user was logged into a COW but not using it) since the beginning of the simulation

% increment time by 1
incrementTime(Amount)
:- time(Time), NewTime is Time + Amount, retract(time(X)), assert(time(NewTime)).

% increment completion time
incrementCompletionTime(User, IncrementTime)
:- completionTime(User, CompletionTime), NewCompletionTime is CompletionTime + IncrementTime, retract(completionTime(User, X)), assert(completionTime(User, NewCompletionTime)).


% set the amount of time that the COW has been unattended
setInactivityDuration(Action, ActionTime)
:- member(Action, [logIntoCOW(User, COW), useCOWAfterLogIn(User, COW), useCOWAfterMove(User, COW), useCOWAfterLeave(User, COW), useCOWAfterMoveSCup(User, COW), useCOWAfterLeaveSCup(User, COW)]), format('resetting inactivity duration.\n'), retract(inactivityDuration(Old)), assert(inactivityDuration(0)), !.
setInactivityDuration(Action, ActionTime)
:- retract(inactivityDuration(Old)), format('adding to inactivity duration for action ~w.\n', [Action]), NewDuration is Old  + ActionTime, assert(inactivityDuration(NewDuration)).

% length of time it takes to carry out various actions
actionTime(logIntoCOW(User, COW), ActionTime) :- ActionTime is 2.
actionTime(useCOWAfterLogIn(User, COW), ActionTime) :- ActionTime is 5 + random(11).
actionTime(moveCOW(User, COW), ActionTime) :- ActionTime is 2 + random(14).
actionTime(useCOWAfterMove(User, COW), ActionTime) :- ActionTime is 5 + random(11).
actionTime(useCOWAfterLeave(User, COW), ActionTime) :- ActionTime is 5 + random(11).
actionTime(useCOWAfterMoveSCup(User, COW), ActionTime) :- ActionTime is 5 + random(11).
actionTime(useCOWAfterLeaveSCup(User, COW), ActionTime) :- ActionTime is 5 + random(11).
actionTime(leaveCOWUnattended(User, COW), ActionTime) :- ActionTime is 1 + random(60).
actionTime(logOut(User, COW), ActionTime) :- ActionTime is 1.
actionTime(takeBreak(User), ActionTime) :- ActionTime is 1 + random(30).

actionTime(placeSCup(User, COW), 1).

inactivityIncrement(moveCOW(User, COW), Increment) :- Increment is 1 + random(5). % takes between 1 and 5 time units
inactivityIncrement(leaveCOWUnattended(User, COW), Increment) :- Increment is 1 + random(20). % takes between 1 and 20 time units
inactivityIncrement(logOut(User, COW), Timeout) :- timeoutDuration(Timeout).

%%%% relating to styrofoam cup placement

updatePlan(Plan, NewPlan)
:- substituteOccurrences(useCOWAfterMove, useCOWAfterMoveSCup, Plan, NewPlan0), substituteOccurrences(useCOWAfterLeave, useCOWAfterLeaveSCup, NewPlan0, NewPlan).

updateFrustration(User, Action)
:- actionFrustration(Action, ActionFrustration), !, modifyFrustration(User, ActionFrustration).

actionFrustration(logIntoCOW(User, COW), 5).
actionFrustration(useCOWAfterLogIn(User, COW), 2).
actionFrustration(moveCOW(User, COW), 10).
actionFrustration(useCOWAfterMove(User, COW), 0) :- isLoggedInto(User,COW), !.
actionFrustration(useCOWAfterMove(User, COW), 50) :- not(isLoggedInto(User,COW)).
actionFrustration(leaveCOWUnattended(User, COW), 2).
actionFrustration(useCOWAfterLeave(User, COW), 0) :- isLoggedInto(User,COW), !.
actionFrustration(useCOWAfterLeave(User, COW), 50) :- not(isLoggedInto(User,COW)).
actionFrustration(logOut(User, COW), 2).

actionFrustration(placeSCup(User, COW), 0).

actionFrustration(useCOWAfterMoveSCup(User, COW), 0).
actionFrustration(useCOWAfterLeaveSCup(User, COW), 0).

actionFrustration(takeBreak(User), 5).

modifyFrustration(User, X) :- frustration(User, Y), Z is X + Y, Z < 0, !, retract(frustration(User, Y)), assert(frustration(User, 0)), format('changed frustration for user ~w from ~w to 0.\n', [User, Y, 0]).
modifyFrustration(User, X) :- frustration(User, Y), Z is X + Y, !, retract(frustration(User, Y)), assert(frustration(User, Z)), format('changed frustration for user ~w from ~w to ~w.\n', [User, Y, Z]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

createEnvironment(K, L, M)
:- createUsers(K),
createCOWs(L),
assert(numUsers(K)),
assert(numCOWs(L)),
assert(timeoutDuration(M)).  % duration of time before an automatic timeout occurs

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment values and probabilities

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

initialFrustrationRange(0, 100).
frustrationThresholdRange(100, 200).
probabilityWorkaroundKnowledge(1).

% to add:
% probability good/bad user (regarding logging out and logging others out)... should this really be good/bad or a spectrum?
% anger temperament
% anger reactionary

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
initSCupWorkaroundKnowledge(User),
initCompletionTime(User).


initFrustration(User) :- initialFrustrationRange(Min, Max), chooseInRange(Min, Max, Frustration), assert(frustration(User, Frustration)).

initPeakFrustration(User) :- frustration(User, Frustration), assert(peakFrustration(User, Frustration)).

initSCupWorkaroundKnowledge(User) :- probabilityWorkaroundKnowledge(P), chooseWithProbability(P, 1), !, assert(sCupWorkaroundKnowledge(User)).
initSCupWorkaroundKnowledge(User).

initCompletionTime(User) :- assert(completionTime(User, -1)).

initFrustrationThreshold(User) :- frustrationThresholdRange(Min, Max), chooseInRange(Min, Max, Threshold), assert(frustrationThreshold(User, Threshold)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% COWs

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

createCOWs(K)
:- K > 1, KMinusOne is K - 1, createCOW(KMinusOne), createCOWs(KMinusOne).
createCOWs(1)
:- createCOW(0).

createCOW(COW)
:- assert(cow(COW)),                   % create cow
assert(inactivityDuration(COW, 0)),    % how long the cow has been inactive
assert(charge(COW, 100)).              % how much charge the cow carries

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% interaction information

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%% interaction information regarding people and COWs
% isLoggedInto(User, COW).          % this is set iff User is logged into COW
% isInteractingWith(User, COW).     % this is set iff User is interacting with COW (used to determine whether timeout occurs)
% inactivityDuration(COW, Time).    % the duration of time for which the COW has not been used.
% sCupPlaced(COW)                   % this is set iff COW has a styrofoam cup placed on its proximity sensor

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% goals

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% always do work-- only implemented goal.
goal(doWork).
goalWeight(doWork, 1).

% subgoals
subGoal(performFirstStep(Plan)).
subGoal(decidePerformRest(Plan)).

subGoal(myDecide(_)).

% new subgoals
subGoal(acquireAccessToCOW).

% primitive actions... may want to expand some to subgoals such as leaveRoom
primitiveAction(logIntoCOW(User, COW)) :- runningUser(User), findCOW(0, COW).
primitiveAction(useCOWAfterLogIn(User, COW)) :- runningUser(User).
primitiveAction(moveCOW(User, COW)) :- runningUser(User).
primitiveAction(useCOWAfterMove(User, COW)) :- runningUser(User).
primitiveAction(leaveCOWUnattended(User, COW)) :- runningUser(User).
primitiveAction(useCOWAfterLeave(User, COW)) :- runningUser(User).
primitiveAction(logOut(User, COW)) :- runningUser(User), isLoggedInto(User, COW).

primitiveAction(placeSCup(User, COW)) :- runningUser(User).


primitiveAction(useCOWAfterMoveSCup(User, COW)) :- runningUser(User).
primitiveAction(useCOWAfterLeaveSCup(User, COW)) :- runningUser(User).

primitiveAction(takeBreak(User)) :- runningUser(User).

% helper for prim action log into cow
findCOW(I, COW) :- numCOWs(K), I < K, not(isLoggedInto(User, I)), COW is I, !.
findCOW(I, COW) :- numCOWs(K), I < K, IPlusOne is I + 1, findCOW(IPlusOne, COW), !.


% the work plan
plan(User, [logIntoCOW(User, COW), useCOWAfterLogIn(User, COW), moveCOW(User, COW), useCOWAfterMove(User, COW), moveCOW(User, COW), useCOWAfterMove(User, COW), moveCOW(User, COW), useCOWAfterMove(User, COW), leaveCOWUnattended(User, COW), useCOWAfterLeave(User, COW), moveCOW(User, COW), useCOWAfterMove(User, COW),leaveCOWUnattended(User, COW), useCOWAfterLeave(User, COW), logOut(User, COW), takeBreak(User), logIntoCOW(User, COWB), useCOWAfterLogIn(User, COWB), moveCOW(User, COWB), useCOWAfterMove(User, COWB), moveCOW(User, COWB), useCOWAfterMove(User, COWB), moveCOW(User, COWB), useCOWAfterMove(User, COWB), leaveCOWUnattended(User, COWB), useCOWAfterLeave(User, COWB), moveCOW(User, COWB), useCOWAfterMove(User, COWB), logOut(User, COWB)]).

goalRequirements(myDecide(performFirstStep([Action|Rest])), [placeSCup(User, COW), Action])
:- runningUser(User), isLoggedInto(User, COW), not(sCupPlaced(COW)), sCupWorkaroundKnowledge(User), format('determining whether to place styrofoam cup before action ~w...\n', [Action]), frustration(User, Frustration), frustrationThreshold(User, Threshold), Frustration > Threshold, ansi_format([fg(red)], 'I am frustrated and so I will place a styrofoam cup over the proximity sensor as my next action.\n', []).

goalRequirements(myDecide(performFirstStep([Action|Rest])), [Action]).

goalRequirements(doWork, [myDecide(performFirstStep(Plan)), decidePerformRest(Plan)])
:- format('checking plan...\n'), runningUser(User), !, plan(User, Plan), format('expanding goal requirements of doWork.\n').

goalRequirements(performFirstStep([Action|Rest]), [Action])
:- format('expanding goal requirements for performFirstStep(~w|Rest) in plan ~w.\n', [Action,[Action|Rest]]).

goalRequirements(decidePerformRest([H|R]), [myDecide(performFirstStep(R)), decidePerformRest(R)]).
goalRequirements(decidePerformRest([]), [doNothing]).

addSets(Action, _, _, [[1.0, performed(Action)]]).

% utility measure... similar to regular utility measure but we also subtract off the frustration

utility(World, Utility) :- runningUser(User), sumUtility(World, NetActionUtility), frustration(User, UserFrustration), Utility is NetActionUtility - UserFrustration.

% placing a strofoam cup costs 60
actionCost(placeSCup(User, COW), 40)
:- !.

% every other action costs 10
actionCost(_, 10).

% every action has a value of 50
actionValue(_, 50).

% mental model of a user
mentalModel([user]).

% choose action that yields maximum utility
decisionTheoretic.

% world is initially empty
worldState([]).

% copy/paste from bcma
% Similarly you must have a trigger to avoid a crash.
trigger(World, _, [World], 0).  % by default, nothing happens when a world enters a particular state.

inWorld(Action, World) :- member(performed(Action), World).
