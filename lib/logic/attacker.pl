% -*- Mode: Prolog -*-

% Agent to simulate attacks

% Current status: initial implementation. Uses nmap, rabidsqrl and sqlmap,
% with these interfaces defined on the body side in Action.java

:- style_check(-singleton).
:- style_check(-discontiguous).

:- dynamic(performed/1).
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
goalWeight(readFile('127.0.0.1','/etc/passwd'),1).

% Main goal to find the database users on a site, if it has a database
%goalWeight(showDBUsers('testphp.vulnweb.com'),1).
%goalWeight(showDBUsers('127.0.0.1'),1).

% One possible top-level goal is to install the agent on a target host
goal(agentUploaded(_)).

% Another is to read a file from a host
goal(readFile(_,_)).

% Features of a host
% findOS(Host,Os) - subgoal of finding OS of a host
% knowOS(Host,Os) - agent knows OS of host
% OSs currently used below: windowsXP_SP2, macOS10 (versioning to be made formal)
% 
% findArch(Host,Arch) - subgoal of finding the architecture of a host
% knowArch(Host,Arch) - agent knows arch
% Archs currently mentioned: i386 (not yet used to choose attacks)
%
% findService(Host,Service) - subgoal to detect host is running a service
% knowServices(H,Services) - agents knows a list of services the host is running
% Services are structured objects that include ports
% Services currently used below: mysql (needs a generalization to sql services)
%
% findVulnerability(Host,Service,Vuln) - subgoal to find a vulnerability through a service
% A 'vulnerability' is a construct that indicates a certain kind of attack might work
% An example is sql(Port,Baseurl,Param), which works through an http service
%  and can be exploited by rabidsqrl, sqlmap and others.

subGoal(findOS(_,_)).
subGoal(findService(_,_)).
subGoal(findVulnerability(_,_,_)).
subGoal(findArch(_,_)).

% Some more specific subgoals that are common
subGoal(findSQLVuln(Host)). % Find a vulnerable sql vulnerability on a host

% The ms() wrapper around the actions tells the java shell
% to use the metasploit interface (uses our internal SQL injection
% interface for that part).

% Characterize alternative actions by information they provide, to
% make this simpler. The second argument shows which argument of the
% action is the host being exploited or learned about.

exploit(hpOpenView(_,X),X).  % in metasploit, not currently implemented
exploit(macOpenView(_,X),X). % in metasploit, not currently implemented
exploit(sqlInjectionReadFile(_,X,File,Port,Baseurl,Parameter),X). % uses rabidsqrl and mysqlmap
exploit(sqlInjectionShowUsers(_,X,Port,Baseurl,Parameter),X). % uses rabidsqrl and mysqlmap
osLearner(bannerGrabber(X),X).            % in metasploit, not currently implemented
serviceLearner(portScanner(X,Path),X).         % uses nmap
vulnerabilityLearner(sqlmap(X,Port,Baseurl,Param),X,sql(Port,Baseurl,Param)). % sqlmap

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

% Can show DB users on a machine running a sql service that's vulnerable through a web form
goalRequirements(showDBUsers(Host),
		 [findSQLVuln(Host), verifyVulnerability(Host,sql(Port,BaseUrl,Parameter),V), 
		  ms(sqlInjectionShowUsers(Y,Host,Port,BaseUrl,Parameter))])
  :- agentUploaded(Y), reachable(Host,Y).

% It may be possible to use an sql injection attack to read a file,
% if the target machine is running a vulnerable server

% Mark as done if the action was performed
goalRequirements(readFile(X,File), [doNothing]) :- performed(ms(sqlInjectionReadFile(Y,X,File,Port,Base,Param))).

% One way to read a file is via an sql injection if available. Alternative ways to read a file could
% be specified with additional clauses.
goalRequirements(readFile(Target,File), 
                 [findSQLVuln(Target), verifyVulnerability(Target,sql(Port,BaseUrl,Parameter),0),
		  ms(sqlInjectionReadFile(AttackLoc,Target,File,Port,BaseUrl,Parameter))])
  :- agentUploaded(AttackLoc), reachable(Target,AttackLoc), format('Seeking an SQL vulnerability on ~w to read ~w~n', [Target,File]).

% Can do the same with an alternative service 
% (the returned term from the port scanner is port(Port,'http-alt') - used to be 'http-alt'(Port)).
goalRequirements(findSQLVuln(Host), 
		 [findService(Host,port(Port,Protocol)), findVulnerability(Host, http(Port,Protocol), sql(Port,BaseUrl,Parameter))])
  :- likelyVulnerability(Host, Port, BaseUrl, Parameter).

% One way to find a vulnerable sql port is to look for a vulnerable mysql service
%goalRequirements(findSQLVuln(Host), 
%		 [findService(Host,port(Port,http)), findVulnerability(Host, http(Port), sql(Port,BaseUrl,Parameter))])
%  :- likelyVulnerability(Host, Port, BaseUrl, Parameter).

% Can do the same with a proxy-service (the returned term from the port scanner is 'http-proxy'(Port)).
%goalRequirements(findSQLVuln(Host), 
%		 [findService(Host,port(Port,'http-proxy')), findVulnerability(Host, http(Port), sql(Port,BaseUrl,Parameter))])
%  :- likelyVulnerability(Host, Port, BaseUrl, Parameter).


% One way to upload a local agent is by OpenView remote buffer overflow, if the
% DASH agent already determined the operating system was appropriate
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

goalRequirements(findService(X,S),[]) :- format('looking for ~w~n', [S]), knowServices(X,L), member(S,L), 
					 format('know service ~w~n', [S]).

goalRequirements(findService(X,S), [ms(portScanner(X,Path)), verifyService(X,S)]) :-
    absolute_file_name(path('nmap'),Path).


goalRequirements(findArch(X,A), []) :- knowArch(X,A).

% Don't repeat work finding vulnerabilities
goalRequirements(findVulnerability(X,S,V),[]) :- knowVulnerability(X, S, V).

% sqlmap can be used to find a vulnerability in a mysql server or web interface (as well as others)
goalRequirements(findVulnerability(X,http(Port,Protocol),sql(Port,Base,Param)),
		 [ms(sqlmap(X,Port,Base,Param)),verifyVulnerability(X,sql(Port,Base,Param),0)]) :-  % 0 is success for a vulnerability learner.
    member(Protocol,['sun-answerbook', 'http-alt','http-proxy',http]).   % Check the recorded protocol is one we might expect to respond to http requests

% As we represent more information about the actions we might
% need to expand these updateBeliefs clauses.

updateBeliefs(ms(Act),0) 
  :- exploit(Act,_), !, format('Succeeded with exploit ~w~n', [Act]), addToWorld(performed(ms(Act))). % , addToWorld(agentUploaded(X)).
updateBeliefs(ms(Act),_) 
  :- exploit(Act,_), format('Exploit ~w failed~n', [Act]), addToWorld(performed(ms(Act))). % , addToWorld(agentUploaded(X)).
%updateBeliefs(ms(Act), 0) % 0 is success in some of the actions, e.g. sqlmap
%  :- addToWorld(performed(ms(Act))), !, fail.
updateBeliefs(ms(Act), OSResult) 
  :- osLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowOS(X, OSResult)), 
     assert(knowOS(X,OSResult)).
updateBeliefs(ms(Act), ServiceResult) 
  :- serviceLearner(Act,X), addToWorld(performed(ms(Act))), addToWorld(knowServices(X, ServiceResult)).
     %assert(knowServices(X,[sql(3306)])).
updateBeliefs(ms(Act), VulnResult)
  :- vulnerabilityLearner(Act,X,S), addToWorld(performed(ms(Act))), addToWorld(knowVulnerability(X, S, VulnResult)),
     format('vulnerability result for ~w was ~w~n', [[Act,X,S], VulnResult]),
     assert(knowVulnerability(X,S,VulnResult)).
updateBeliefs(doNothing,_).  % The doNothing action always succeeds. The updateBeliefs predicate should always succeed 
                             % but I want to catch every sitation so haven't added a catchall clause.

execute(verifyOS(Host,OS)) :- knowOS(Host,OS).
execute(verifyService(Host,Service)) :- knowServices(Host,L), member(Service,L).
execute(verifyVulnerability(Host,Service,Vuln)) :- knowVulnerability(Host,Service,Vuln).

addToWorld(Fact) :- initialWorld(I), retract(initialWorld(I)), assert(initialWorld([Fact|I])), assert(Fact). %, format('asserted ~w~n',[Fact]).


% In the initial world, the agent can only run code on its own host computer.
agentUploaded(localhost).
initialWorld([agentUploaded(localhost)]).
reachable('127.0.0.1',localhost).   % To test a one-hop plan without pivoting
reachable('testphp.vulnweb.com',localhost).

% To make things simple while putting stuff in place, everything's an intel box
knowArch(_,i386).

% And to make things simple, we already know a likely sql vulnerability on the target machine.
% This may have come from e.g. google dork or from a human sniffing around, which we 
% still need to simulate in an agent model.
likelyVulnerability('testphp.vulnweb.com',80,'listproducts.php','cat').
% A local simple server defined in python, vulnerable to mysql injection attacks
likelyVulnerability('127.0.0.1',80,'index.html','name').
likelyVulnerability('127.0.0.1',8888,'hackme.php','select').  % Could be guessed from the form on the index.html page


