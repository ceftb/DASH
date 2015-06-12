% -*- Mode: Prolog -*-

% Agent to simulate attacks

% Current status: initial implementation.

% 

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(knowOS/2).

:-consult('agentGeneral').

% Treating one mode of attack as top level for now to
% flesh it out.
goal(runningOn(_)).
goalWeight(runningOn(targetMachine),1).

subGoal(findOS(_,_)).

% The ms() wrapper around the actions tells the java shell
% to use the metasploit interface (uses our internal SQL injection
% interface for that part).
primitiveAction(ms(hPOpenView(_))).
primitiveAction(ms(macOpenView(_))).
primitiveAction(ms(bannerGrabber(_))).
primitiveAction(doNothing).

executable(verifyOS(_,_)).

% Do nothing if the top level goal is already achieved
goalRequirements(runningOn(X), [doNothing]) :- initialWorld(I), member(runningOn(X),I).


% One way to get on is HO OpenView remote buffer overflow, if the
% agent already determined the operating system was appropriate
goalRequirements(runningOn(X), [findOS(X,windows(xp,sp2)), ms(hPOpenView(X))]).

% An alternate approach on MacOS10
goalRequirements(runningOn(X), [findOS(X,macOS10), ms(macOpenView(X))]).

% If you already know the OS, findOS succeeds on that OS and fails on
% all others.
goalRequirements(findOS(X,OS), []) :- knowOS(X,OS).

% One way to determine the OS is by inspecting the banner on a set of
% ports. Here this is abstracted by the BannerGrabber primitive.
goalRequirements(findOS(X,OS), [ms(bannerGrabber(X)), verifyOS(X,OS)]).

% Bin alternative actions by information they provide to make this
% simpler. As we represent more information about the actions we might
% need to expand these updateBeliefs clauses.

exploit(hpOpenView(X),X).
exploit(macOpenView(X),X).
osLearner(bannerGrabber(X),X).

updateBeliefs(ms(Act),1) 
  :- exploit(Act,X), addToWorld(performed(ms(Act))), addToWorld(runningOn(X)).
updateBeliefs(ms(Act), 0) 
  :- addToWorld(performed(ms(Act))), !, fail.
updateBeliefs(ms(Act), OSResult) 
  :- osLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowOS(X, OSResult)), 
     assert(knowOS(X,OSResult)).

execute(verifyOS(Host,OS)) :- knowOS(Host,OS).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).



initialWorld([]).

