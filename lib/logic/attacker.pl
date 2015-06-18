% -*- Mode: Prolog -*-

% Agent to simulate attacks

% Current status: initial implementation.

% 

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(knowOS/2).
:- dynamic(knowArch/2).
:- dynamic(agentUploaded/1).

:-consult('agentGeneral').

% Treating one mode of attack as top level for now to
% flesh it out.
goal(agentUploaded(_)).
goalWeight(agentUploaded(targetMachine),1).

subGoal(findOS(_,_)).
subGoal(findArch(_,_)).

% The ms() wrapper around the actions tells the java shell
% to use the metasploit interface (uses our internal SQL injection
% interface for that part).
primitiveAction(ms(hpOpenView(_,_))).
primitiveAction(ms(macOpenView(_,_))).
primitiveAction(ms(bannerGrabber(_))).

executable(verifyOS(_,_)).

% Do nothing if the top level goal is already achieved
goalRequirements(agentUploaded(X), [doNothing]) :- initialWorld(I), member(agentUploaded(X),I).


% One way to get on is HO OpenView remote buffer overflow, if the
% agent already determined the operating system was appropriate
goalRequirements(agentUploaded(X), [findOS(X,windowsXP_SP2), findArch(X,i386), ms(hpOpenView(Y, X))])
  :- agentUploaded(Y).

% An alternate approach on MacOS10
goalRequirements(agentUploaded(X), [findOS(X,macOS10), ms(macOpenView(Y,X))])
  :- agentUploaded(Y).

% If you already know the OS, findOS succeeds on that OS and fails on
% all others.
goalRequirements(findOS(X,OS), []) :- knowOS(X,OS).

% One way to determine the OS is by inspecting the banner on a set of
% ports. Here this is abstracted by the BannerGrabber primitive.
goalRequirements(findOS(X,OS), [ms(bannerGrabber(X)), verifyOS(X,OS)]).

goalRequirements(findArch(X,A), []) :- knowArch(X,A).


% Bin alternative actions by information they provide to make this
% simpler. As we represent more information about the actions we might
% need to expand these updateBeliefs clauses.

exploit(hpOpenView(_,X),X).
exploit(macOpenView(_,X),X).
osLearner(bannerGrabber(X),X).

updateBeliefs(ms(Act),1) 
  :- exploit(Act,X), addToWorld(performed(ms(Act))), addToWorld(agentUploaded(X)).
updateBeliefs(ms(Act), 0) 
  :- addToWorld(performed(ms(Act))), !, fail.
updateBeliefs(ms(Act), OSResult) 
  :- osLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowOS(X, OSResult)), 
     assert(knowOS(X,OSResult)).

execute(verifyOS(Host,OS)) :- knowOS(Host,OS).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).


% Agent begins able to run things on its own PC.
agentUploaded(localhost).
initialWorld([agentUploaded(localhost)]).

% To make things simple while putting stuff in place, everything's an intel box
knowArch(_,i386).
