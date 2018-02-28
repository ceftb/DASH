% -*- Mode: Prolog -*-

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF GOAL REQUIREMENTS----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

% Goal = initialize
% These used to be the initialization requirements for a worker agent, not an IT agent.
%goalRequirements(initialize,	[getOnComputer(ID),
%				computer_applicationCloseAll(void),
%				continueInitialize1,
%				computer_applicationOpen(outlook),
%				continueInitialize2]).
%	:-	machineName(ID).
%
%goalRequirements(continueInitialize1,	[printMessage('Closed All Windows\n')])
%	:-	succeeded(computer_applicationCloseAll(_)), !.
%
%goalRequirements(continueInitialize1,	[printMessage('Failed to close all Windows\n')]).
%
%goalRequirements(continueInitialize2,	[printMessage('Opened Outlook\n'),
%					communicate_onlineEmailSend(2, 'www.zulu.isp/index.html'),
%					continueInitialize3])
%	:-	succeeded(computer_applicationOpen(outlook)), !.
%
%goalRequirements(continueInitialize2,	[printMessage('Failed to Open Outlook')]).
%
%goalRequirements(continueInitialize3,	[printMessage(Message)])
%	:-	succeeded(communicate_onlineEmailSend(Agent,Message)), !
%                sformat(Message, 'Email message: ~w , send to ~w \n', [Message, Agent]).
%
%goalRequirements(continueInitialize3,	[printMessage('Email Failed\n')]).

goalRequirements(initialize, []).

% Goal = doWork

goalRequirements(doWork, [printMessage('Processing new request\n'),processRequestExecutable])
       :- taskFixPCRequest(_).

goalRequirements(doWork,	[printMessage('IT Agent is going over to diagnose the problem, but has other jobs on queue\n'),
				 updateAgentState(happiness, -0.1),
				 callBack])
	:-	tiredness(Tiredness), tasks(Jobs), overWorkedThreshold(Threshold),
		Tiredness < Threshold, Jobs > 40, !.

goalRequirements(doWork,	[printMessage('IT Agent is going over to diagnose the problem\n'),
				updateAgentState(happiness, -0.1),
				callBack])
	:-	tiredness(Tiredness), tasks(Jobs), overWorkedThreshold(Threshold),
		Tiredness < Threshold, Jobs > 0, !.

goalRequirements(doWork,	[
				doNothing
			        ])
	:-	tiredness(Tiredness), overWorkedThreshold(Threshold),
		Tiredness < Threshold, !,
		tiring(doWork, TiringValue).

goalRequirements(doWork,	[printMessage('IT Agent is too tired to work\n'), doNothing]).

% Goal = checkPC
goalRequirements(checkPC,	[getOnComputer(ID),
				executableCheckPC1,
				printMessage('IT Agent Succeeded to diagnose a problem\n'),
				continueCheckPC])
	:-	diagnoseSuccessThreshold(DST),
		techCompetency(TC),
		taskFixPC(ID),
		ranf(RandomFloat),
		Temp is RandomFloat + TC,
		DST < Temp, !.

goalRequirements(checkPC,	[getOnComputer(ID),
				printMessage('IT Agent Failed to diagnose a problem\n'),
				getOffComputer])
	:-	taskFixPC(ID).

goalRequirements(continueCheckPC,	[executableCheckPC2,
					callPerson(ID, response(bugFixed)),
					removeJobFromStack,
					printMessage('IT Agent fixed the problem\n'),
					updateAgentState(tiring, TiringValue),
					getOffComputer])
	:-	repairSuccessThreshold(RST),
		techCompetency(TC),
		ranf(RandomFloat),
		Temp is RandomFloat + TC,
		RST < Temp, !,
		taskFixPC(ID),
		tiring(continueCheckPC, TiringValue).

goalRequirements(continueCheckPC,	[printMessage('IT Agent failed to fix the computer\n'),
					getOffComputer]).
		
% Goal = callBack

goalRequirements(callBack, [checkPC])  % Receive a request to look at a PC rather than a spreadsheet error
        :- taskFixPC(_), !.

goalRequirements(callBack, 	[callPerson(ID, error(Type, [Spreadsheet, Row, Col])),
				removeJobFromStack,
				updateAgentState(tiring, TiringValue),
				printMessage(Message),
				continueCallBack(Type, [Spreadsheet, Row, Col], ID)])
	:-	errorLog(Type, [Spreadsheet, Row, Col], ID), !,
		tiring(callBack, TiringValue),
		tiredness(Tiredness),
		sformat(Message, 'Tiring: ~w\n', [Tiredness]).

goalRequirements(callBack,	[printMessage('No Errors to Fix\n')]).

goalRequirements(continueCallBack(Type, Spreadsheet, Row, Col, ID),	[removeErrorLog(Type, Spreadsheet, Row, Col, ID)]).

% Goal = FixError
goalRequirements(fixError(errorLog(spreadsheetValue, Spreadsheet, Row, Col, ID)),
	             [addPredicate(errorLog(spreadSheetValue, Spreadsheet, Row, Col, ID)),
		     addJobToStack,
		     updateAgentState(tiring, TiringValue),
		     printMessage(Message)])
	:-	tiring(fixError,TiringValue),
		tiredness(Tiredness),
		sformat(Message, 'Tiredness: ~w\n', [Tiredness]), !.

goalRequirements(fixError(errorLog(Type, Spreadsheet, Row, Col, ID)),	[addPredicate(errorLog(Type, Spreadsheet, Row, Col, ID)),
									addJobToStack,
									updateAgentState(tiring, TiringValue1),
									callPerson(ID, response(humanError)),
									printMessage(Type),
									removeErrorLog(Type, Spreadsheet, Row, Col, ID),
									removeJobFromStack,
									updateAgentState(tiring, TiringValue2)])
	:-	tiring(addJobToStack, TiringValue1), tiring(removeJobFromStack, TiringValue2).


% Goal = RespondToMessage
goalRequirements(respondToMessage(errorLog(Type, S, R, V), ID),	[fixError(errorLog(Type, S, R, V, ID))]).

goalRequirements(respondToMessage(fixed(_, _, _)),	[printMessage('Agent fixed his computer\n')]).

goalRequirements(respondToMessage(Predicate),	[addPredicate(Predicate),
						addJobToStack,
						updateAgentState(tiring, TiringValue),
						printMessage(Message)])
	:-	tiring(addJobToStack, TiringValue),
		tiredness(Tiredness),
		sformat(Message, 'Tiredness: ~w\n', [Tiredness]).

%-------------
% Effects of actions, in terms of updated beliefs
%-------------

updateBeliefs(_,_).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%-----------------------------LIST OF Executables-------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
executable(romoveErrorLog(_, _,_,_, _)).
execute(romoveErrorLog(Type, Spreadsheet, Row, Col, ID)) :- myRetract(errorLog(Type, Spreadsheet, Row, Col, ID)).

executable(insertErrorLog(_,_)).
execute(insertErrorLog(Error, Value)) :- myAssert(tempError(Error, Value)).

executable(executableCheckPC1).
execute(executableCheckPC1) :-	myAssert(pcDiagnosed(true)). %check to see where this predicate is retracted!

executable(executableCheckPC2).
execute(executableCheckPC2) :- myAssert(pcFixed(true)). %check to see where this predicate is retracted!

executable(processRequestExecutable).
execute(processRequestExecutable)
  :- taskFixPCRequest(ID), myRetract(taskFixPCRequest(ID)), myAssert(taskFixPC(ID)), 
     tasks(N), New is N + 1, myRetract(tasks(N)), myAssert(tasks(New)).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF Primitive Actions----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

primitiveAction(computer_applicationCloseAll(void)).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Subgoals---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
subGoal(checkPC).
subGoal(callBack).
subGoal(fixError(errorLog(_,_,_,_,_))).

subGoal(continueInitialize).
subGoal(continueCheckPC).
subGoal(continueCallBack).


:-dynamic(computer_applicationCloseAll/1).

:-dynamic(tempError/2).
:-dynamic(pcDiagnosed/1).
:-dynamic(pcFixed/1).
:-dynamic(errorLog/3).

:-dynamic(taskFixPCRequest/1).
