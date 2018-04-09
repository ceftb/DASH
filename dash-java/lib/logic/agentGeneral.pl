% -*- Mode: Prolog -*-

:- style_check(-singleton).
:- style_check(-discontiguous).

:-consult('system1').
:-consult('system2').
:-consult('perception').

%-----------
% Multifile
%-----------
:- multifile executable/1.
:- multifile execute/1.
:- multifile primitiveAction/1.
:- multifile goalRequirements/2.
:- multifile subGoal/1.
:- multifile repeatable/1.
:- multifile belief/2.
:- multifile succeeded/1.
:- multifile updateBeliefs/1.
:- multifile updateBeliefs/2.
:- multifile state/1.
:- multifile goal/1.

% Simulates the basic interaction with the agent
test(Time) :- do(Action), format('~w\n', [Action]), assert(result(Action, 1, Time)).

%% The rest of this file handles reactive planning

%------------
% do(Action)
%------------

% This is the fundamental step, so it calls system 1.
do(Action) :-
	perception,
	updateBeliefs,
	system1,
	chooseAction(Action).
	%printAllAdded.

chooseAction(Action) :-
	chooseGoal(G),
	chooseAction([G], Action).


chooseGoal(G) :- 
	findall([C,W], goalWeight(C,W), List), 
	maxList(List, G).

chooseAction([G|T], Action) :- 
	goalRequirements(G, L),
	nextAction([G|T], L, Action).


nextAction([G|RestOfG], [H|T], Action) :- 
	not(repeatable(H)), done(G, H), !, 
	nextAction([G|RestOfG], T, Action).

% Simpler version
nextAction(GoalList, [H|T], Action) :-
        executable(H), !, execute(H),
	system1, % The world changed, let system1 have another go
        nextAction(GoalList, T, Action).  % Just go through the actions

nextAction([G|RestOfG], [H|_], H) :- 
	primitiveAction(H), !,
	goalRequirements(G, L), 
	markAction([G|RestOfG], L, H).

nextAction([G|RestOfG], [H|_], Action) :- 
	subGoal(H),
	append([H], [G|RestOfG], NewList),
	chooseAction(NewList, Action).

nextAction([G|RestOfG], [], Action) :-
	checkGoal([G|RestOfG], []), 
	chooseAction(Action).  % was do, but want to skip updateBeliefs


markAction([G|T], L, Action) :- 
	myAssert(done(G, Action)),
	checkGoal([G|T], L).


checkGoal([G|RestOfG], [H|T]) :- 
	done(G, H), !, 
	checkGoal([G|RestOfG], T).

checkGoal([G|RestOfG], []) :- 
	not(goal(G)), !, 
	head(RestOfG, G2),
	myAssert(done(G2, G)),
	myRetractall(done(G, _)),
	myRetractall(choice(G, _)),
	goalRequirements(G2, L),
	checkGoal(RestOfG, L).

checkGoal([G|_], []) :-
	goal(G), !, myRetractall(done(G, _)).

checkGoal(_, _).

% Some interesting output

printAllAdded :-
  findall(P,added(P),L),
  printAll(L).

printAll([]).
printAll([H|T]) :- format('~w\n',[H]), printAll(T).

%-----------------
% Update beliefs based on the last action performed
%-----------------

updateBeliefs :- 
        findall([[A,S],T],result(A,S,T),L), 
	maxList(L,[A,S]),
        updateBeliefs(A,S).

% If nothing has happened yet.
updateBeliefs :- findall([A,T],result(A,_,T),[]).

% Since the general code switches callPerson into a phone call or whatever,
% the specific agent code shouldn't have to register belief updates for
% each different communication mode
updateBeliefs(commPhone_outCall(Agent, Message), ReturnValue)
  :- !, updateBeliefs(callPerson(Agent, Message), ReturnValue).

updateBeliefs(commSet(Variable, Value), 1)
  :- !, myAssert(sharedValue(Variable, Value)).
updateBeliefs(commSet(Variable, Value), _).

updateBeliefs(commGet(Variable), Value) :- myAssert(sharedValue(Variable, Value)).


%------------------
% Utility predicates
%------------------
head([H|T], H).

maxList([[HG,HW]|T], M) :- maxListR(T, HG, HW, M).

maxListR([], BestG, BestW, BestG).
maxListR([[HeadG,HeadWeight]|T], BestG, BestWeight, M) 
  :- HeadWeight > BestWeight,  maxListR(T, HeadG, HeadWeight, M).
maxListR([[_,HeadWeight]|T], BestG, BestWeight, M)     
  :- HeadWeight =< BestWeight, maxListR(T, BestG, BestWeight, M).

ranf(X) :-     
	N = 65536,
	X is random(N)/N.

myAssert(Term) :- retract(deleted(Term)), !, asserta(Term), asserta(added(Term)).
myAssert(Term) :- asserta(Term), asserta(added(Term)).

myRetract(Term) :- retract(added(Term)), !, retract(Term), asserta(deleted(Term)).
myRetract(Term) :- retract(Term), asserta(deleted(Term)).

myRetractall(Term) :- findall(Term, Term, List), retractList(List).

retractList([H|T]) :- myRetract(H), retractList(T).
retractList([]).

assertValue(X, Y) :- retractall(value(X,_)), assert(value(X,Y)).

% Simplify a lot of 'asserta' calls
check(Goal) :- call(Goal), asserta(visited(Goal)).

% Simplify result > 0 calls
succeeded(Action) :- result(Action,R,_), R > 0.

% Default tiringness for any task
tiring(0.1).
tiring(Task,Val) :- tiring(Val).


%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF GOAL REQUIREMENTS----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%


% Waiting (usually for the 'start' button on the DASHboard)
goal(waiting).
goalRequirements(waiting, [doNothing]).

% These largely come from the old NCR application and are no longer used.

%----------------------
% Goal = addJobToStack
%----------------------
goalRequirements(addJobToStack,	[incrementTask(Tasks),
				printMessage(Message)])
	:-	check(tasks(Tasks)),
		NewTasks is Tasks + 1,
		sformat(Message, 'Tasks Left ~w\n', [NewTasks]).


%---------------------------
% Goal = removeJobFromStack
%---------------------------
goalRequirements(removeJobFromStack,	[decrementTasks,   % removed task argument so agent will recognize when it has done it. This is not a proper solution, will need to revisit.
					 printMessage('Tasks Left: ~w\n', [NewTasks])])
	:-	check(tasks(Tasks)), NewTasks is Tasks -1.

%-------------------
% Goal = callPerson 
%-------------------
goalRequirements(callPerson(ID, Message),	[commPhone_outCall(ID, Message),
						continueCallPerson(ID, Message)]).

goalRequirements(continueCallPerson(ID, SentMessage),	[printMessage(Message)])
	:-	succeeded(commPhone_outCall(ID,SentMessage)), !,
		sformat(Message, 'Message ~w sent to: ~w\n', [SentMessage, ID]).

goalRequirements(continueCallPerson(ID, SentMessage),	[printMessage('Call Failed\n')])
        :-      result(commPhone_outCall(ID,SentMessage),R,_), R =< 0.


%----------------------
% Goal = getOnComputer
%----------------------
goalRequirements(getOnComputer(ID),	[computer_using(ID),
	                                 continueGetOnComputer1]).

goalRequirements(continueGetOnComputer1,	[computer_login,
						continueGetOnComputer2])
	:-	succeeded(computer_using(_)), !.

goalRequirements(continueGetOnComputer1,	[printMessage('Didn\'t start using computer\n')]).

goalRequirements(continueGetOnComputer2,	[printMessage('Successfully logged in to computer\n')])
	:-	succeeded(computer_login), !.

goalRequirements(continueGetOnComputer2,	[printMessage('Didn\'t log into computer\n')]).


%-----------------------
% Goal = getOffComputer
%-----------------------
goalRequirements(getOffComputer, [computer_logout, continueGetOffComputer1]).

goalRequirements(continueGetOffComputer1, [computer_leave, continueGetOffComputer2])
	:-	succeeded(computer_logout), !.

goalRequirements(continueGetOffComputer1, [printMessage('Unable to log out\n')]).

goalRequirements(continueGetOffComputer2, [printMessage('Able to logout and leave computer\n'),
					   logOffComputer])
	:-	succeeded(computer_leave), !.

goalRequirements(continueGetOffComputer2, 
	[printMessage('Logged out but couldn\'t leave the computer\n')]).




%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%-----------------------------LIST OF Executables-------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

executable(addPredicate(_)).
execute(addPredicate(Predicate)) :- myAssert(Predicate).

executable(goToSleep(_)).
execute(goToSleep(Seconds)) :- sleep(Seconds).

executable(printMessage(_)).
% Clause left for legacy in case there are some of these around
execute(printMessage(Number)) :- message(Number, Message), !, print(Message).
execute(printMessage(Message)) :- sformat(Fullmessage, 'Agent: ~s', [Message]), print(Fullmessage).

executable(printMessage(_,_)).
execute(printMessage(MessageString,Arguments)) :- 
  sformat(Message, MessageString, Arguments), execute(printMessage(Message)).

executable(decrementTasks).
execute(decrementTasks) :- check(tasks(Tasks)), myRetract(tasks(Tasks)), NewTasks is Tasks-1, myAssert(tasks(NewTasks)).

executable(incrementTasks(Tasks)).
execute(incrementTasks(Tasks)) :- myRetract(tasks(Tasks)), NewTasks is Tasks+1, myAssert(tasks(NewTasks)).

executable(logOffComputer).
execute(logOffComputer) :- myRetract(logOffComp(_)), myAssert(logOffComp(true)), myRetractall(okToWork(true)).

executable(updateAgentState(_, _)).
% Convenient shorthand
execute(updateAgentState(tiredness,Action)) :- 
   atom(Action), !, tiring(Action,Tiringness), agentState(tiredness, Current), 
   New is Current + Tiringness,
   execute(updateAgentState(tiredness,New)).
execute(updateAgentState(Field, Value)) :- myRetractall(agentState(Field,_)), myAssert(agentState(Field,Value)).

% Take a list of key-value pairs and update.
executable(updateAgentState(_)).
execute(updateAgentState([])).
execute(updateAgentState([[Field,Value]|T]))
  :- execute(updateAgentState(Field,Value)), execute(updateAgentState(T)).

executable(factorAgentState(_,_,_)).

% Field f is something, like unexpectedness, that increases towards some asymptote A,
% where A - f decreases exponentially to 0 with Factor as the multiplier.
execute(factorAgentState(Field, Asymptote, Factor)) :-
  agentState(Field, Old),
  New is Asymptote + (Old - Asymptote) * Factor,
  format('~w is now ~w after factor update \n', [Field, New]),
  execute(updateAgentState(Field, New)).

executable(reportAgentState).
execute(reportAgentState)
	:- 	agentState(tiredness, Tiredness),
		format('And I am now tired at level ~w\n', [Tiredness]), 
		agentState(unexpectedness, Unexpectedness),
		format('Unexpectedness was ~w\n', [Unexpectedness]).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF Primitive Actions----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

% This is domain-independent. The ability to spawn another agent should usually
% only be used by the group agent.
primitiveAction(startAgent(AgentFileName)).

primitiveAction(commPhone_outCall(ID, Message)).

primitiveAction(commGet(Variable,Value)).
primitiveAction(commSet(Variable,Value)).

% These are from an older implementation of using a computer from NCR.
% I want to implement this more generally by setting and getting state
% on the comms server. See commSet and commGet above.
primitiveAction(computer_using(ID)).

primitiveAction(computer_login).

primitiveAction(computer_logout).

primitiveAction(computer_leave).

primitiveAction(doNothing).  % Should be a subgoal that turns into emailing, going to the web, 'sleeping' etc.

primitiveAction(pause(_)).  % pause n milliseconds, implemented in the body

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Subgoals---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

subGoal(callPerson(_, _)).
subGoal(removeJobFromStack).
subGoal(addJobToStack).
subGoal(initialize).
subGoal(getOnComputer(_)).
subGoal(getOffComputer).

subGoal(continueCallPerson(ID, Message)).
subGoal(continueGetOnComputer1).
subGoal(continueGetOnComputer2).
subGoal(continueGetOffComputer1).
subGoal(continueGetOffComputer2).

% Shared state
commsHost('localhost').


%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Dynamics---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

:-dynamic(done/2).
:-dynamic(choice/2).
:-dynamic(visited/1).
:-dynamic(added/1).
:-dynamic(deleted/1).
:-dynamic(message/2).
:-dynamic(result/3).
:-dynamic(error/1).
:-dynamic(response/1).
:-dynamic(id/1).

:-dynamic(commPhone_outCall/3).
:-dynamic(sharedValue/2).
:-dynamic(computer_using/2).
:-dynamic(computer_login/1).
:-dynamic(computer_logout/1).
:-dynamic(computer_leave/1).

:-dynamic(machineName/1).
:-dynamic(tasks/1).
:-dynamic(evil/1).
:-dynamic(okToWork/1).
:-dynamic(agentState/2).
:-dynamic(uIPredicates/1).

% Set by the 'start' button. Since I would like arbitrary buttons, I need
% a 'button' predicate that is dynamic, I think.
:-dynamic(started/0).

uIPredicates([]).
