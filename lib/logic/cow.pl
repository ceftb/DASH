%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
% scout's good doobie/bad doobie idea... related: "good" users may log out other users. bad users may not.
% sean's reusable COWs idea-- a styrofoam cup that has been placed on a COW may affect multiple users... related: is there any value of thinking of information exchange of workaround knowledge more technically (e.g. bell lapadula model).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(worldState/1).
:- dynamic(frustration/1).
:- dynamic(time/1).
:- dynamic(sCupUsed/1).
:- dynamic(isLoggedInto/2).
:- dynamic(isInteractingWith/2).
:- dynamic(inactivityDuration/2).
:- dynamic(completionTime/2).
:- dynamic(knowledge/2).
:- dynamic(netExposure/1).
:- dynamic(sCupPlaced/1).
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
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time is CompletionTime + 1, retractall(isInteractingWith(User, COW)), format('updating beliefs.\n'), updateBeliefs, format('engaging system1.\n'), system1, format('choosing action.\n'), chooseAction(Action), updateFrustration(Action), actionTime(Action, ActionTime), incrementCompletionTime(User, ActionTime), completionTime(User, NewCompletionTime), format('User ~w: performed action ~w with result 1 starting at time ~w. Will complete action at time ~w.\n', [User, Action, Time, NewCompletionTime]), updateSCup(Action), format('updating state of world.\n'), actionUpdate(Action), format('adding action to world.\n'), addToWorld(Action), !.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time =< CompletionTime, format('User ~w: Still in process of carrying out last action.\n', User), !.
runUserIteration(User) :- setUser(User), time(Time), completionTime(User, CompletionTime), Time >= CompletionTime, format('User ~w: Idling.\n', User), !.

%%%% set current user
setUser(User)
    :- retractall(runningUser(_)), assert(runningUser(User)).

%%%% updateWorld
updateWorld :- updateCOWs(0).

%%%% call updateCOW for each COW.
updateCOWs(COW) :- numCOWs(K), COW < K, updateCOW(COW), NextCOW is COW + 1, updateCOWs(NextCOW), !.
updateCOWs(COW) :- numCOWs(K), COW = K.

%%%% update the COW
% if no user is logged into COW, do nothing.
% if a user is interacting with a COW, we also need to do nothing.
% else, increment inactivity duration for that cow.
updateCOW(COW) :- not(isLoggedInto(User, COW)), !.
updateCOW(COW) :- isInteractingWith(User, COW), !.
updateCOW(COW) :- not(sCupPlaced(COW)), isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), NewTime is Timeout, retract(isLoggedInto(User, COW)), retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)), ansi_format([fg(green)], 'Timeout has occurred on COW ~w.\n', [COW]), !.
updateCOW(COW) :- sCupPlaced(COW), isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), NewTime is Timeout, retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)), !.
updateCOW(COW) :- isLoggedInto(User, COW), not(isInteractingWith(User, COW)), inactivityDuration(COW, Time), NewTime is Time + 1, timeoutDuration(Timeout), not(NewTime is Timeout), retract(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, NewTime)), retract(netExposure(NetExposure)), NewNetExposure is NetExposure + 1, assert(netExposure(NewNetExposure)),!.
updateCOW(COW) :- format('Trying to update COW ~w: we should not be here.\n', COW).

%%%% one iteration - OLD
%oneIteration :- time(Time), completionTime(CompletionTime), Time is CompletionTime + 1, format('updating beliefs.\n'), updateBeliefs, format('engaging system1.\n'), system1, format('choosing action.\n'), chooseAction(Action), updateFrustration(Action), incrementTime(1), actionTime(Action, ActionTime), incrementCompletionTime(User, ActionTime), completionTime(NewCompletionTime), format('performed action ~w with result 1 starting at time ~w. Will complete action at time ~w.\n', [Action, Time, NewCompletionTime]), updateSCup(Action), format('setting inactivity duration.\n'), setInactivityDuration(Action, ActionTime), format('adding action to world.\n'), addToWorld(Action), !.
%oneIteration :- time(Time), completionTime(CompletionTime), Time =< CompletionTime, format('Still in process of carrying out last action.\n'), incrementTime(1), !.
%oneIteration :- time(Time), completionTime(CompletionTime), Time >= CompletionTime, format('Idling.\n'), incrementTime(1), !.

%%%% multiple iterations - OLD
% kIterations(K) :- integer(K), K > 1, oneIteration, KMinusOne is K - 1, kIterations(KMinusOne).
% kIterations(1) :- oneIteration.

%%%% one iteration - OLD
% oneIteration :- time(Time), completionTime(CompletionTime), Time is CompletionTime + 1, format('updating beliefs.\n'), updateBeliefs, format('engaging system1.\n'), system1, format('choosing action.\n'), chooseAction(Action), updateFrustration(Action), incrementTime(1), actionTime(Action, ActionTime), incrementCompletionTime(ActionTime), completionTime(NewCompletionTime), format('performed action ~w with result 1 starting at time ~w. Will complete action at time ~w.\n', [Action, Time, NewCompletionTime]), updateSCup(Action), format('setting inactivity duration.\n'), setInactivityDuration(Action, ActionTime), addToWorld(Action), !.
% oneIteration :- time(Time), completionTime(CompletionTime), Time =< CompletionTime, format('Still in process of carrying out last action.\n'), incrementTime(1), !.
% oneIteration :- time(Time), completionTime(CompletionTime), Time >= CompletionTime, format('Idling.\n'), incrementTime(1), !.
% oneIteration :- format('Error: This statement should never appear.\n').

%%%% update world based on the action.
actionUpdate(logIntoCOW(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(useCOWAfterLogIn(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterMove(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterLeave(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterMoveSCup(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).
actionUpdate(useCOWAfterLeaveSCup(User, COW)) :- retractall(isLoggedInto(User, COW)), assert(isLoggedInto(User, COW)), assert(isInteractingWith(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(moveCOW(User, COW)). % retracting is interacting with is done automatically
actionUpdate(leaveCOWUnattended(User, COW)). % retracting is interacting with is done automatically

actionUpdate(logOut(User, COW)) :- retractall(isLoggedInto(User, COW)), retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)).

actionUpdate(placeSCup(User, COW)) :- retractall(inactivityDuration(COW, Time)), assert(inactivityDuration(COW, 0)), assert(sCupPlaced(COW)).

actionUpdate(Action) :- format('could not update world with action because action ~w was not recognized.\n', Action).

%%%% add action to world
addToWorld(Action)
    :- worldState(Current), retract(worldState(Current)), addToEnd(Current, performed(Action), NewWorld), assert(worldState(NewWorld)).

addToEnd([H|R], Item, [H|NewList])
    :- addToEnd(R, Item, NewList).

addToEnd([], Item, [Item]).

%%%% things regarding timing: world time, timeout duration, etc.

time(0).                        % initial time is 0
timeoutDuration(15).            % duration of time before an automatic timeout occurs
netExposure(0).                 % net exposure (total time units that a user was logged into a COW but not using it) since the beginning of the simulation

% increment time by 1
incrementTime(Amount)
    :- time(Time), NewTime is Time + Amount, retract(time(X)), assert(time(NewTime)).

% increment completion time
incrementCompletionTime(User, IncrementTime)
:- completionTime(User, CompletionTime), NewCompletionTime is CompletionTime + IncrementTime, retract(completionTime(User, X)), assert(completionTime(User, NewCompletionTime)).

%incrementCompletionTime(IncrementTime)
%:- completionTime(CompletionTime), NewCompletionTime is CompletionTime + IncrementTime, retract(completionTime(X)), assert(completionTime(NewCompletionTime)).

% set the amount of time that the COW has been unattended
setInactivityDuration(Action, ActionTime)
    :- member(Action, [logIntoCOW(User, COW), useCOWAfterLogIn(User, COW), useCOWAfterMove(User, COW), useCOWAfterLeave(User, COW), useCOWAfterMoveSCup(User, COW), useCOWAfterLeaveSCup(User, COW)]), format('resetting inactivity duration.\n'), retract(inactivityDuration(Old)), assert(inactivityDuration(0)), !.
setInactivityDuration(Action, ActionTime)
    :- retract(inactivityDuration(Old)), format('adding to inactivity duration for action ~w.\n', [Action]), NewDuration is Old  + ActionTime, assert(inactivityDuration(NewDuration)).

% length of time it takes to carry out various actions
actionTime(logIntoCOW(User, COW), ActionTime) :- ActionTime is 2.
actionTime(useCOWAfterLogIn(User, COW), ActionTime) :- ActionTime is 5 + random(15).
actionTime(moveCOW(User, COW), ActionTime) :- ActionTime is 2 + random(8).
actionTime(useCOWAfterMove(User, COW), ActionTime) :- ActionTime is 5 + random(15).
actionTime(useCOWAfterLeave(User, COW), ActionTime) :- ActionTime is 5 + random(15).
actionTime(useCOWAfterMoveSCup(User, COW), ActionTime) :- ActionTime is 4 + random(15).
actionTime(useCOWAfterLeaveSCup(User, COW), ActionTime) :- ActionTime is 4 + random(15).
actionTime(leaveCOWUnattended(User, COW), ActionTime) :- ActionTime is 1 + random(29).
actionTime(logOut(User, COW), ActionTime) :- ActionTime is 1.

actionTime(placeSCup(User, COW), 1).

inactivityIncrement(moveCOW(User, COW), Increment) :- Increment is 1 + random(5). % takes between 1 and 5 time units
inactivityIncrement(leaveCOWUnattended(User, COW), Increment) :- Increment is 1 + random(20). % takes between 1 and 20 time units
inactivityIncrement(logOut(User, COW), Timeout) :- timeoutDuration(Timeout).

%%%% relating to styrofoam cup placement

updateSCup(placeSCup(User, COW)) :- not(sCupPlaced(COW)), assert(sCupPlaced(COW)), !.
updateSCup(Action).                                                                    

updatePlan(Plan, NewPlan)
    :- substituteOccurrences(useCOWAfterMove, useCOWAfterMoveSCup, Plan, NewPlan0), substituteOccurrences(useCOWAfterLeave, useCOWAfterLeaveSCup, NewPlan0, NewPlan).

updateFrustration(Action)
    :- actionFrustration(Action, ActionFrustration), !, modifyFrustration(ActionFrustration).

actionFrustration(logIntoCOW(User, COW), 20).
actionFrustration(useCOWAfterLogIn(User, COW), 10).
actionFrustration(moveCOW(User, COW),30).
actionFrustration(useCOWAfterMove(User, COW), 0) :- isLoggedInto(User,COW), !.
actionFrustration(useCOWAfterMove(User, COW), 0) :- not(isLoggedInto(User,COW)).
%actionFrustration(useCOWAfterMove(User, COW), 0) :- sCupPlaced(COW), !.
%actionFrustration(useCOWAfterMove(User, COW), 0) :- inactivityDuration(X), timeoutDuration(Timeout), X =< Timeout, !.
%actionFrustration(useCOWAfterMove(User, COW), 40) :-  not(sCupPlaced(COW)).
actionFrustration(leaveCOWUnattended(User, COW), 5).
actionFrustration(useCOWAfterLeave(User, COW), 0) :- isLoggedInto(User,COW), !.
actionFrustration(useCOWAfterLeave(User, COW), 0) :- not(isLoggedInto(User,COW)).
%actionFrustration(useCOWAfterLeave(User, COW), 0) :-  sCupPlaced(COW), !.
%actionFrustration(useCOWAfterLeave(User, COW), 0) :- inactivityDuration(X), timeoutDuration(Timeout), X =< Timeout, !.
%actionFrustration(useCOWAfterLeave(User, COW), 50) :-  not(sCupPlaced(COW)).
actionFrustration(logOut(User, COW), 5).

actionFrustration(placeSCup(User, COW), 0).

actionFrustration(useCOWAfterMoveSCup(User, COW), 0).
actionFrustration(useCOWAfterLeaveSCup(User, COW), 0).

% frustration is initially 0. Certain actions may increase or decrease it.
frustration(0).
modifyFrustration(X) :- frustration(Y), !, Z is X + Y, retract(frustration(Y)), assert(frustration(Z)), format('changed frustration from ~w to ~w.\n', [Y, Z]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% environment

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


createEnvironment(K, L)
    :- createUsers(K),
    createCOWs(L),
    assert(numUsers(K)),
    assert(numCOWs(L)).

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
    :- assert(user(User)),                              % create user
    assert(sCupWorkaroundKnowledge(User)),              % all users know about the workaround... need to change this later
    assert(completionTime(User, -1)).                   % completion time of latest action

%%%% knowledge and skills for workaround... should be an attribute of the user
knowledge(sCupWorkaround, 1). % the workaround can only be used if the user knows how to perform it

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
    :- assert(cow(COW)).

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

% to do
% add primitive actions:
%    interact with patient
%    plug COW battery charger into wall outlet
%    incorporate spread of workaround knowledge... certain actions should provide knowledge of a workaround if it is seen

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
primitiveAction(logOut(User, COW)) :- runningUser(User).

primitiveAction(placeSCup(User, COW)) :- runningUser(User).


primitiveAction(useCOWAfterMoveSCup(User, COW)) :- runningUser(User).
primitiveAction(useCOWAfterLeaveSCup(User, COW)) :- runningUser(User).

% helper for prim action log into cow
findCOW(I, COW) :- numCOWs(K), I < K, not(isLoggedInto(User, I)), COW is I, !.
findCOW(I, COW) :- numCOWs(K), I < K, IPlusOne is I + 1, findCOW(IPlusOne, COW), !.


% the work plan
plan(User, [logIntoCOW(User, COW), useCOWAfterLogIn(User, COW), moveCOW(User, COW), leaveCOWUnattended(User, COW), useCOWAfterLeave(User, COW), logOut(User, COW)]).

goalRequirements(myDecide(performFirstStep([Action|Rest])), [placeSCup(User, COW), Action])
    :- runningUser(User), isLoggedInto(User, COW), not(sCupPlaced(COW)), sCupWorkaroundKnowledge(User), worldState(I), !, format('determining whether to place styrofoam cup before action ~w...\n', [Action]), updatePlan(Rest, UpdatedRest), preferPlan([placeSCup(User, COW), Action | UpdatedRest], [Action | Rest], I), ansi_format([fg(red)], 'I am frustrated and so I will place a styrofoam cup over the proximity sensor as my next action.\n', []).

goalRequirements(myDecide(performFirstStep([Action|Rest])), [Action]).

%goalRequirements(myDecide(performFirstStep([Action|Rest])), [Action]).
%    :- worldState(I), format('calling preferPlan starting with action ~w.\n', [Action]), preferPlan([Action|Rest], Rest, I), format('finished calling preferPlan\n').

%goalRequirements(myDecide(Action), [])
%    :- format('Action ~W not chosen and no other action chosen.\n', Action).

% to do work we attempt to carry out the plan.
goalRequirements(doWork, [myDecide(performFirstStep(Plan)), decidePerformRest(Plan)])
    :- format('checking plan...\n'), runningUser(User), !, plan(User, Plan), format('expanding goal requirements of doWork.\n').
goalRequirements(doWork, [doNothing]). % i do not think we need this

% perform first step of plan
goalRequirements(performFirstStep([Action|Rest]), [Action])
    :- format('expanding goal requirements for performFirstStep(~w|Rest) in plan ~w.\n', [Action,[Action|Rest]]).

% if there are no more steps required to carry out the plan, we need not do anything.
% else, we should decide whether or not to carry out the remaining steps.
goalRequirements(decidePerformRest([]), [doNothing]).
% goalRequirements(decidePerformRest([H|R]), [decide(performFirstStep(R)), decidePerformRest(R)]).
goalRequirements(decidePerformRest([H|R]), [myDecide(performFirstStep(S)), decidePerformRest(S)])
    :- runningUser(User), isLoggedInto(User, COW), sCupPlaced(COW), updatePlan(R, S), !.
goalRequirements(decidePerformRest([H|R]), [myDecide(performFirstStep(R)), decidePerformRest(R)])
    :- runningUser(User), not(isLoggedInto(User, COW)).
goalRequirements(decidePerformRest([H|R]), [myDecide(performFirstStep(R)), decidePerformRest(R)])
    :- runningUser(User), isLoggedInto(User, COW), not(sCupPlaced(COW)).

% recall that decide(X) carries out the action X iff ok(X) is a fact
% so, here, we are saying that system 2 tells us to perform an action if we prefer performing the action
% to not performing the action. 
%system2Fact(ok(performFirstStep([Action|Rest])))
%		 :- initialWorld(I), format('calling preferPlan starting with action ~w.\n', [Action]), preferPlan([Action|Rest], Rest, I), format('finished calling preferPlan\n').
%		 :- incr(envision), initialWorld(I), preferPlan([Action|Rest], Rest, I).

% addSets... these specify what facts are added to the world
% upon completion of actions. I do not completely understand how this works yet.
% update... I moved the frustration modification in the result portion
% addSets(Action, _, _, [[1.0, performed(Action)]]) :- format('addSets called with action ~w\n', [Action]).
addSets(Action, _, _, [[1.0, performed(Action)]]).

% utility measure... similar to regular utility measure but we also subtract off the frustration

utility(World, Utility) :- sumUtility(World, NetActionUtility), frustration(UserFrustration), Utility is NetActionUtility - UserFrustration.

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

% cost is really frustration + cost
sumUtility([], 0).
%sumUtility([performed(A)|Rest], Utility) :- format('called recursive sum utility with head ~w, action ~w... utility at this depth is ~w.\n', [Head, Action, V - C - F + URest]), actionCost(A, C), actionFrustration(A, F), actionValue(A, V), !, sumUtility(Rest, URest), Utility is V - C - F + URest.
%sumUtility([H|R],S) :- !, sumUtility(R, S), format('called recursive sum utility with head ~w but could not identify action at this depth... utility at this depth is ~w.\n', [H, S]).
sumUtility([performed(A)|Rest], Utility) :- actionCost(A, C), actionFrustration(A, F), actionValue(A, V), !, sumUtility(Rest, URest), Utility is V - C - F + URest.
sumUtility([H|R],S) :- !, sumUtility(R, S).