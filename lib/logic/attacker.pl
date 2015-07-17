% -*- Mode: Prolog -*-

% Agent to simulate attacks

% Current status: initial implementation.

% 

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(field/2).
:- dynamic(initialWorld/1).
:- dynamic(knowOS/2).
:- dynamic(knowServices/2).
:- dynamic(knowArch/2).
:- dynamic(knowVulnerability/3).
% agentUploaded(X) means the exploit agent is loaded on machine X.
:- dynamic(agentUploaded/1).
% reachable(X,Y) means host Y is reachable from X.
:- dynamic(reachable/2).

:-consult('agentGeneral').

% The main goal for this run is to install the agent on the targetMachine
%goalWeight(agentUploaded(targetMachine),1).

% The main goal for this run is to read a file on the target machine
goalWeight(readFile(targetMachine,'/tmp/passwd'),1).

% One possible top-level goal is to install the agent on a target host
goal(agentUploaded(_)).

% Another is to read a file from the host
goal(readFile(_,_)).

subGoal(findOS(_,_)).
subGoal(findService(_,_)).
subGoal(findVulnerability(_,_,_)).
subGoal(findArch(_,_)).

% The ms() wrapper around the actions tells the java shell
% to use the metasploit interface (uses our internal SQL injection
% interface for that part).

% Characterize alternative actions by information they provide, to
% make this simpler. The second argument shows which argument of the
% action is the host being exploited or learned about.

exploit(hpOpenView(_,X),X).  % in metasploit, not currently implemented
exploit(macOpenView(_,X),X). % in metasploit, not currently implemented
exploit(sqlInjectionReadFile(_,X,_,_),X). % uses rabidsqrl
osLearner(bannerGrabber(X),X).            % in metasploit, not currently implemented
serviceLearner(portScanner(X),X).         % uses nmap
vulnerabilityLearner(sqlmapproject(X,sql(P)),X,sql(P)). % sqlmapproject

% Exploits, serviceLearners and osLearners and vulnerabilityLearners are kinds of primitive actions.
primitiveAction(ms(T)) :- exploit(T,_).
primitiveAction(ms(T)) :- osLearner(T,_).
primitiveAction(ms(T)) :- serviceLearner(T,_).
primitiveAction(ms(T)) :- vulnerabilityLearner(T,_,_).

executable(verifyOS(_,_)).
executable(verifyService(_,_)).
executable(verifyVulnerability(_,_,_)).

% Do nothing if the top level goal is already achieved
goalRequirements(agentUploaded(X), [doNothing]) 
  :- initialWorld(I), member(agentUploaded(X),I).

% It may be possible to use an sql injection attack to read a file,
% if the target machine is running a vulnerable server
goalRequirements(readFile(X,File), [findService(X,sql(Port)), findVulnerability(X,sql(Port),V), ms(sqlInjectionReadFile(Y,X,Port,File))])
  :- agentUploaded(Y), reachable(X,Y).

% One way to get on is by OpenView remote buffer overflow, if the
% agent already determined the operating system was appropriate
goalRequirements(agentUploaded(X), [findOS(X,windowsXP_SP2), findArch(X,i386), ms(hpOpenView(Y, X))])
  :- agentUploaded(Y), reachable(X,Y).

% An alternate approach on MacOS10
goalRequirements(agentUploaded(X), [findOS(X,macOS10), ms(macOpenView(Y,X))])
  :- agentUploaded(Y), reachable(X,Y).


% If you already know the OS, findOS succeeds on that OS and fails on
% all others.
goalRequirements(findOS(X,OS), []) :- knowOS(X,OS).

% One way to determine the OS is by inspecting the banner on a set of
% ports. Here this is abstracted by the BannerGrabber primitive.
goalRequirements(findOS(X,OS), [ms(bannerGrabber(X)), verifyOS(X,OS)]).

goalRequirements(findService(X,S),[]) :- knowServices(X,L), member(S,L).

goalRequirements(findService(X,S), [ms(portScanner(X)), verifyService(X,S)]).


goalRequirements(findArch(X,A), []) :- knowArch(X,A).

% sqlmapproject can be used to find a vulnerability in a sql server or web interface
goalRequirements(findVulnerability(X,sql(P),V),[]) :- knowVulnerability(X, sql(P), V).

goalRequirements(findVulnerability(X,sql(P),V),[ms(sqlmapproject(X,sql(P))),verifyVulnerability(X,sql(P),V)]).

% As we represent more information about the actions we might
% need to expand these updateBeliefs clauses.

updateBeliefs(ms(Act),1) 
  :- exploit(Act,X), addToWorld(performed(ms(Act))), addToWorld(agentUploaded(X)).
updateBeliefs(ms(Act), 0) 
  :- addToWorld(performed(ms(Act))), !, fail.
updateBeliefs(ms(Act), OSResult) 
  :- osLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowOS(X, OSResult)), 
     assert(knowOS(X,OSResult)).
updateBeliefs(ms(Act), ServiceResult) 
  :- serviceLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowServices(X, ServiceResult)),
     assert(knowServices(X,[sql(3306)])).
updateBeliefs(ms(Act), VulnResult) 
  :- vulnerabilityLearner(Act,X,S), addToWorld(performed(ms(Act))), addToWorld(knowVulnerability(X, S, VulnResult)),
     assert(knowVulnerability(X,S,VulnResult)).

execute(verifyOS(Host,OS)) :- knowOS(Host,OS).
execute(verifyService(Host,Service)) :- knowServices(Host,L), member(Service,L).
execute(verifyVulnerability(Host,Service,Vuln)) :- knowVulnerability(Host,Service,Vuln).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact).


% In the initial world, the agent can only run code on its own host computer.
agentUploaded(localhost).
initialWorld([agentUploaded(localhost)]).
reachable(targetMachine,localhost).   % To test a one-hop plan without pivoting

% To make things simple while putting stuff in place, everything's an intel box
knowArch(_,i386).
