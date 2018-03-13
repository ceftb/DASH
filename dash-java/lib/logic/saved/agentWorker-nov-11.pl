% -*- Mode: Prolog -*-

% Removing much of the 'continue' style to use automatic continuations 
% based on re-trying with diminishing expectations.
% Right now the 'continues' are good as a way to look up the result
% of past actions and pass them on, not as a way to describe error recovery.

:- style_check(-singleton).
:- style_check(-discontiguous).

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF GOAL REQUIREMENTS----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

%---------------
% Goal = doWork
%---------------
goalRequirements(doWork, [doEvilWork])
	:-	check(evil(true)), !.


%-------------------
% Goal = doEvilWork
%-------------------
goalRequirements(doEvilWork, [RequirementList])
	:-	findall((Spreadsheet, Size), taskFillSpreadsheet(Spreadsheet, Size, false), Spreadsheets),
		corruptall(Spreadsheets, RequirementList).

corruptall([(Spreadsheet, Size)|T], RequirementList)
	:-	getOffset(Spreadsheet, Offset),
		corrupt(Spreadsheet, Size, Offset, List1),
		corruptall(T, List2),
		append(List1, List2, RequirementList).

corruptall([], []).

corrupt(_, 0, _, []).

corrupt(Spreadsheet, Row, Offset, RequirementList)
	:-	TaskID is Row+Offset,
		check(finishedTask(TaskID)), !,
		NextRow is Row - 1,
		corrupt(Spreadsheet, NextRow, Offset, RequirementList).

corrupt(Spreadsheet, Row, Offset, RequirementList)
	:-	NextRow is Row - 1,
		corrupt(Spreadsheet, NextRow, Offset, List1),
		SRow is Row + Offset,
		append([changeValue(Spreadsheet, SRow, count, 0)], List1, RequirementList).

getOffset(supp, 104).
getOffset(shipment, 0).
getOffset(_, 0).



%--------------------
% Goal = changeValue
%--------------------
goalRequirements(changeValue(Spreadsheet, Row, Col, Value), [toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							     toolsForWorkflow_spreadsheetSetValue(Value, Row, Col),
							     continueChangeValue]).

goalRequirements(continueChangeValue,	[updateAgentState(frustrated, 0.1),
					 updateAgentState(tiredness, continueChangeValue),
					 updateAgentState(unexpectedness, 0.05)])
	:-	succeeded(toolsForWorkflow_spreadsheetSetValue(_)), !.

goalRequirements(continueChangeValue,	[printMessage('Failed to set value\n')]).


%---------------
% Goal = doWork
%---------------
goalRequirements(doWork, [doOrdinaryWork])
	:-	check(evil(false)).


%-----------------------
% Goal = doOrdinaryWork
%-----------------------

%goalRequirements(doOrdinaryWork, [checkInsertedValue])
%        :-      insertedValues(_,_,_,_), trace, checkSpreadsheetChance(P), N is random(100)/100, N < P, !.

% If unexpectedness is too high, something is wrong - call IT
goalRequirements(doOrdinaryWork, [doNothing]) :-
	check(agentState(unexpectedness,U)), U > 0.8, myIT(IT), result(commPhone_outCall(IT,_),_,_), !. % Just call IT once, then wait

goalRequirements(doOrdinaryWork, [callPerson(IT, 'please fix my machine')]) :-
	check(agentState(unexpectedness,U)), U > 0.8, myIT(IT), !.

goalRequirements(doOrdinaryWork, [taskFillCell(Spreadsheet, Row, Col)])
	:-	check(agentState(unexpectedness,U)), U =< 0.8, check(taskFillCell(Spreadsheet, Row, Col)), 
		!.

goalRequirements(doOrdinaryWork, [doNothing]).  % If no work to do.


%---------------------------
% Goal = checkInsertedValue
%---------------------------
goalRequirements(checkInsertedValue, [removeOpenSpreadsheet,
				      openSpreadsheet,
				      check(ChosenS, ChosenR, ChosenC, ChosenV)])
	:-	findall((Spreadsheet, Row, Col, Value), insertedValues(Spreadsheet, Row, Col, Value), List),
                pickRandom(List, (ChosenS, ChosenR, ChosenC, ChosenV)),
		format('** will check (~w, ~w, ~w) is ~w\n', [ChosenS, ChosenR, ChosenC, ChosenV]).

pickRandom(List, E) :- length(List, Length), N is random(Length), nth0(N, List, E).

goalRequirements(check(Spreadsheet, Row, Col, Value),	[toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							continueCheck1(Spreadsheet),
							toolsForWorkflow_spreadsheetIsValue(Value, Row, Col),
							continueCheck2(Spreadsheet, Row, Value)]).

goalRequirements(continueCheck1(Spreadsheet),	[printMessage('Opened Spreadsheet ~w\n', [Spreadsheet])])
	:-	succeeded(toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet)), !.

goalRequirements(continueCheck1(Spreadsheet),	[printMessage('Failed to Open Spreadsheet ~w\n', [Spreadsheet])]).

goalRequirements(continueCheck2(Spreadsheet, Row, Value), [checkExecutable,
							   printMessage('Spreadsheet Value at row ~w is value ~w, as expected\n', [Row, Value])])
	:-	succeeded(toolsForWorkflow_spreadsheetIsValue(Value, Row, _)), !.

goalRequirements(continueCheck2(Spreadsheet, Row, Value), [printMessage('Spreadsheet value at row ~w is not value ~w\n', [Row, Value]),
							   respondToError(spreadsheetValue, [(Spreadsheet, Row, Col)]),
							   printMessage('Responded to Error in spreadsheet value\n')]).


%---------------
% Goal = doTask
%---------------

goalRequirements(taskFillCell(Spreadsheet, Row, Col), [delegateTask(taskFillCell(Spreadsheet, Row, Col))])
	:-	check(agentState(tiredness, Tiredness)),
	        check(overWorkedThresh(OverWorked)),
		Tiredness > OverWorked, !.

goalRequirements(taskFillCell(Spreadsheet, Row, Col), [lookUpAndInsert(Spreadsheet, Row, Col)]).


%---------------------
% Goal = delegateTask
%---------------------
goalRequirements(delegateTask(Task),  [callPerson(ID, Task), continueDelegateTask(Task, ID)])
	:-	check(agentWorker(ID)).

% If delegating failed, do nothing on the assumption that one will become less tired.
goalRequirements(delegateTask(Task), [printMessage('delegating failed, taking a break'), doNothing]).


goalRequirements(continueDelegateTask(Task, _),	[updateAgentState(tiredness, continueDelegateTask),
						 retractTask(Task),
						 removeJobFromStack])
	:-	succeeded(commPhone_outCall(Task)), !.

goalRequirements(continueDelegateTask(Task, ID), [printMessage('Coworker ~w is not answering phone\n', [ID])]).
						

%------------------------
% Goal = lookUpAndInsert
%------------------------
goalRequirements(lookUpAndInsert(Spreadsheet, Row, Col), [getValues(Spreadsheet, Row, Col), 
                                                          openSpreadsheet,
							  insertValues(Spreadsheet, Row, Col),
							  reportAgent,
							  removeJobFromStack,
							  incrementFinishedTask(Spreadsheet, Row, Col),
							  callPerson(Manager, finishedTask(FinishedTask))])
	:-	check(myManager(Manager)),
		check(finishedTasks(FinishedTask)).

%------------------
% Goal = getValues
%------------------
goalRequirements(getValues(Spreadsheet, Row, Col), [openBrowser,
						    readPage(Spreadsheet, Row, Col)])
	:- 	Row < 1000, !.
goalRequirements(getValues(Spreadsheet,Row, Col),  [setUnknownValue(Spreadsheet, Row, Col),
						    printMessage('I don\'t know how to get values for row ~w \n', [Row])]).


%--------------------
% Goal = openBrowser
%--------------------

goalRequirements(openBrowser,	[printMessage('Browser already on top\n')])
	:-	check(browserApp(Browser)), check(appHasFocus(Browser)), !.

% In its original form, this switches to the website while the rule
% above checks that the browser has the focus, so these are out of
% synch. Since the next goal where this is used is 'readPage' which explicitly
% goes to the url, I'm changing this to switch to the browser.
goalRequirements(openBrowser,  [computer_applicationSwitch(Browser),
				continueOpenBrowser1])
	:- 	check(browserApp(Browser)), check(appOpen(Browser)), !.

goalRequirements(openBrowser,	[printMessage('Browser Not Open\n'),
				 computer_applicationOpen(Browser),
				 continueOpenBrowser2])
	:-	check(browserApp(Browser)).

% All this should be obviated by a more reactive representation
goalRequirements(continueOpenBrowser1,	[printMessage('Succeeded in switching to ~w \n', [Browser])])
	:-	succeeded(computer_applicationSwitch(Browser)), !.

goalRequirements(continueOpenBrowser1,	[printMessage('Value of switchApp: ~w\nFailed to switch to website ~w\n', [Result, Website]),
					respondToError(openBrowser, 0),
					printMessage('Responded to Error \'failed to switch to browser\'\n')
				        ])
	:-	result(computer_applicationSwitch(Website), Result, _).

% Now never gets called - if open succeeded, we fire the rule about to switch focus.
%goalRequirements(continueOpenBrowser2,	[updateAgentState(unexpectedness, 0.98),
%					 %openBrowserExecutable3,
%					 printMessage('Browser is open\n')])
%	:-	succeeded(computer_applicationOpen(_)), !.

% This called special code to try to open the browser once more. Taken care of by making open repeatable
% along with some 'frustration' parameter that stops too many attempts.
%goalRequirements(continueOpenBrowser2,	[printMessage('Browser failed to open\n'),
%					 updateAgentState(unexpectedness, 0.02),
%					 respondToError(browserOpen, 0),
%					 printMessage('Responded to error that browser failed to open\n')
%                                         ]).


%-----------------
% Goal = readPage
%-----------------
goalRequirements(readPage(Spreadsheet, Row, Col),	[setCellValue(Spreadsheet, Row, Col),
							 toolsForWorkflow_browserGoToAddress(Web),
							 continueReadPage1(Row, Web)])
	:- 	check(website(Web)), !.
		
goalRequirements(readPage(Spreadsheet, Row, Col),	[setCellValue(Spreadsheet, Row, Col),
							 printMessage('No website known for given task\n')]).

goalRequirements(continueReadPage1(Row, Web), [continueReadPage2(Row)])
	:-	succeeded(toolsForWorkflow_browserGoToAddress(Web)), !. 

goalRequirements(continueReadPage1(_, _),   [printMessage('Go to address failed \n')]).

goalRequirements(continueReadPage2(Row),	[toolsForWorkflow_browserClickLink(LabelName),
						 continueReadPage3(LabelName)])
	:- 	check(taskMap(Row, LabelName)), !.

goalRequirements(continueReadPage2(Row),	[printMessage('No link for given row ~w\n', [Row])]).

goalRequirements(continueReadPage3(LabelName),	[readPageExecutable1,
						 updateAgentState(tiredness, continueReadPage3),
						 printMessage('Looked up Value\n')])
	:-	succeeded(toolsForWorkflow_browserClickLink(LabelName)), !.

goalRequirements(continueReadPage3(LabelName),	[printMessage('Browser clickLink failed\n'),
						 respondToError(clickLink, LabelName),
						 printMessage('Responded to error that clickLink failed\n')]).


%------------------------
% Goal = openSpreadsheet
%------------------------
goalRequirements(openSpreadsheet,	[printMessage('Spreadsheet already on top\n')])
	:-	check(spreadsheetApp(Spreadsheet)),
		check(appHasFocus(Spreadsheet)), !.

goalRequirements(openSpreadsheet,	[computer_applicationSwitch(Spreadsheet),   %'Disaster Riliefe'
					 continueOpenSpreadsheet1])
	:-	check(spreadsheetApp(Spreadsheet)), check(appOpen(Spreadsheet)), !.

goalRequirements(openSpreadsheet,	[toolsForWorkflow_spreadsheetLogin(void),
					continueOpenSpreadsheet2]).

goalRequirements(continueOpenSpreadsheet1,	[printMessage('switch app succeeded: Switched to spreadsheet ~w\n', [Spreadsheet]),
						 %openSpreadsheetExecutable1,
						 updateAgentState(unexpectedness, 0.05)])
	:-	succeeded(computer_applicationSwitch(Spreadsheet)), !.

goalRequirements(continueOpenSpreadsheet1, [printMessage('The value of switchApp: ~w\n', [Result]),
					    printMessage('Failed to switch to spreadsheet\n'),
					    updateAgentState(unexpectedness, 0.9),
					    respondToError(failedSwitchToSpreadsheet, 0),
					    printMessage('Responded to failure to switch to spreadsheet\n')
					    ])
	:-	result(computer_applicationSwitch(disasterRelief), Result, _).

goalRequirements(continueOpenSpreadsheet2,	[openSpreadsheetExecutable3,
						 updateAgentState(unexpectedness, 0.05),
						 printMessage('Logged in websheet\n')])
	:-	succeeded(toolsForWorkflow_spreadsheetLogin(_)), !.

goalRequirements(continueOpenSpreadsheet2,	[printMessage('Failed to open spreadsheet\n'),
						 updateAgentState(unexpectedness, 0.9),
						 respondToError(5, 0),
						 printMessage('Responded to error 5\n')
					         ]).


%--------------------
% Goal = insertValue
%--------------------
goalRequirements(insertValues(Spreadsheet, Row, Col),	[toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							continueInsertValue1(Spreadsheet),
							toolsForWorkflow_spreadsheetSetValue(Value, Row, Col),
							continueInsertValue2(Spreadsheet, Row, Col, Value)])
	:- check(cellVal(Spreadsheet, Row, Col, Value)), ranf(Rand), 0.25 < Rand, !.

goalRequirements(insertValues(Spreadsheet, Row, Col),	[toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							continueInsertValue1(Spreadsheet),
							toolsForWorkflow_spreadsheetSetValue(Value, Row, Col),
							continueInsertValue2(Spreadsheet, Row, Col, Value)])
	:- check(cellVal(Spreadsheet, Row, Col, Value)), check(unexpectedness(U)), U < 0.5, !.

goalRequirements(insertValues(Spreadsheet, Row, Col),	[toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet),
							continueInsertValue1(Spreadsheet),
							toolsForWorkflow_spreadsheetSetValue(NewValue, Row, Col),
							continueInsertValue3(Spreadsheet, Row, Col, NewValue)])
	:- check(cellVal(Spreadsheet, Row, Col, Value)), NewValue is Value*10.

goalRequirements(continueInsertValue1(Spreadsheet),	[printMessage('Switched to the correct sheet\n')])
	:-	succeeded(toolsForWorkflow_spreadsheetSwitchSheet(Spreadsheet)), !.

goalRequirements(continueInsertValue1(_),  [printMessage('Failed to switch to the correct sheet\n')]).

goalRequirements(continueInsertValue2(Spreadsheet, Row, Col, Value),	[updateAgentState(frustrated, 0.01),
									updateAgentState(tiredness, continueInsertValue2),
									updateAgentState(unexpectedness, 0.2),
									insertValueExecutable1(Spreadsheet, Row, Col, Value)])
	:-	succeeded(toolsForWorkflow_spreadsheetSetValue(Value,Row,Col)), !. 

goalRequirements(continueInsertValue2(Spreadsheet, Row, Col, Value),	[printMessage('Add Exp Diff ~w\n', [Temporary]),
									updateAgentState(frustrated, 0.01),
									updateAgentState(tiredness, continueInsertValue2),
									updateAgentState(unexpectedness, 0.9),
									printMessage('Warning: was not able to insert value in row ~w\n', [Row])])
	:-	getExpDiff(Temporary).

goalRequirements(continueInsertValue3(Spreadsheet, Row, Col, Value),	[printMessage('Add Exp Diff ~w\n', [Temporary]),
									updateAgentState(frustrated, 0.01),
									updateAgentState(tiredness, continueInsertValue3),
									updateAgentState(unexpectedness, 0.2),
									insertValueExecutable1(Spreadsheet, Row, Col, Value)])
	:-	succeeded(toolsForWorkflow_spreadsheetSetValue(Value,Row,Col)), !,
		getExpDiff(Temporary). 

goalRequirements(continueInsertValue3(Spreadsheet, Row, Col, Value),	[updateAgentState(frustrated, 0.01),
									updateAgentState(tiredness, continueInsertValue3),
									updateAgentState(unexpectedness, 0.9),
									printMessage('Warning: was not able to insert BAD value in row ~w\n', [Row])]).

% Not sure what this is for
getExpDiff(bizarre).


%--------------------
% Goal = reportAgent
%--------------------
goalRequirements(reportAgent, RequirementList)
	:-	findall(insertedValues(Spreadsheet, Row, Col, Value), insertedValues(Spreadsheet, Row, Col, Value), RawList),
		createListInsertedValues(RawList, InsertedValues),
		append(InsertedValues, [reportAgentState], TempReqList),
		machineName(Machine),
		sformat(Message, 'Machine ~w now knows:\n', [Machine]),
		append([printMessage(Message)], TempReqList, RequirementList).

createListInsertedValues([], []).

createListInsertedValues([insertedValues(Spreadsheet, Row, Col, Val)|T], InsertedValues)
	:-	createListInsertedValues(T, TempInsertedValues),
		sformat(Message, 'Inserted ~w in ~w spreadsheet at row ~w col ~w\n', [Val, Spreadsheet, Row, Col]),
		append([printMessage(Message)], TempInsertedValues, InsertedValues).


%-----------------------
% Goal = respondToError
%-----------------------
goalRequirements(respondToError(spreadsheetValue, [Spreadsheet, Row, Col]),	
	          [printMessage('Calling IT to fix error\n'),
		  insertErrorLog(spreadsheetValue, [Spreadsheet, Row, Col]),
		  callPerson(IT, errorLog(spreadsheetValue,Spreadsheet,Row,Col)),  % not sure if I can send nested predicates
		  continueRespondToError(spreadsheetValue, [Spreadsheet, Row, Col])])
	:-	myIT(IT).

goalRequirements(continueRespondToError(spreadsheetValue, _),	[getOffComputer,
						                 updateAgentState(tiredness, continueRespondToError)])
	:-	succeeded(callPerson), !.

goalRequirements(continueRespondToError(spreadsheetValue, _),	[printMessage('Call failed, line busy\n'),
						                 updateAgentState(tiredness, continueRespondToError)]).

goalRequirements(respondToError(openBrowser, 0),	[computer_applicationOpen(Browser),
	                                                 continueRespondToError(openBrowser,0)])
	:- 	check(browserApp(Browser)).

goalRequirements(continueRespondToError(openBrowser, 0),	[updateAgentState(unexpectedness, 0.2),
						 openBrowserExecutable3,
						 printMessage('Browser opened error 2 0 fixed\n'),
						 startWork])
	:-	succeeded(computer_applicationOpen(_)), !.

goalRequirements(continueRespondToError(openBrowser, 0),	[printMessage('Failed to open browser second time\nDO A RESET\n')]).

%I THINK FOR ERROR #2 THE CORRECT RESPONSE SHOULD BE AS FOLLOWS:
%
%goalRequirements(respondToError(2, 0),	[computer_applicationSwitch(http://www.zulu.isp),
%					continueRespondToError(2, 0)]).
%
%goalRequirements(continueRespondToError(2, 0),	[openBrowserExecutable1,
%						updateAgentState(unexpectedness, 0.98)
%						printMessage(1)])
%%	:-	computer_applicationSwitch(http://www.zulu.isp, Result),
%	:-	result(computer_applicationSwitch, Result),
%		Result > 0, !,
%		retractall(message(_, _)), asserta(message(1, 'Switched App Error 2 0 fixed\n')).
%goalRequirements(continueRespondToError(2, 0),	[printMessage(1)])
%	:-	retractall(message(_, _)), asserta(message(1, 'Failed to switch second time\nDO A RESET\n')).

goalRequirements(respondToError(browserOpen, 0),	[computer_applicationOpen(Browser),
					continueRespondToError(browserOpen,0)])
	:- 	check(browserApp(Browser)).

goalRequirements(continueRespondToError(browserOpen, 0),	[updateAgentState(unexpectedness, 0.98),
						openBrowserExecutable3,
						printMessage('Browser Opened Error 3 0 fixed\n')])
	:-	succeeded(computer_applicationOpen), !.

goalRequirements(continueRespondToError(browserOpen, 0),	[printMessage('Failed to open browser second time\nDO A RESET\n')]).

goalRequirements(respondToError(failedSwitchToSpreadsheet, 0),	[toolsForWorkflow_spreadsheetLogin(void),
					continueRespondToError(failedSwitchToSpreadsheet, 0)]).

goalRequirements(continueRespondToError(failedSwitchToSpreadsheet, 0),	[openSpreadsheetExecutable3,
						updateAgentState(unexpectedness, 0.2),
						printMessage('Logged in WebSheet Error 4 0 fixed\n')])
	:-	succeeded(toolsForWorkflow_spreadsheetLogin(void)), !.

goalRequirements(continueRespondToError(failedSwitchToSpreadsheet, 0),	[printMessage('Failed to open spreadsheet second time\nDO A RESET\n')]).

goalRequirements(respondToError(5, 0),	[toolsForWorkflow_spreadsheetLogin(void),
					continureRespondToError(5, 0)]).

goalRequirements(continueRespondToError(5, 0),	[openSpreadsheetExecutable3,
						updateAgentState(unexpectedness, 0.2),
						printMessage('Logged in WebSheet Error 5 0 fixed\n')])
	:-	succeeded(toolsForWorkflow_spreadsheetLogin(void)), !.

goalRequirements(continueRespondToError(5, 0),	[printMessage('Failed to open spreadsheet second time\nDO A RESET\n')]).

goalRequirements(respondToError(clickLink, 0, LabelName),	[toolsForWorkflow_browserClickLink(LabelName),
							         continueRespondToError(clickLink, 0, LabelName)]).

goalRequirements(continueRespondToError(clickLink, 0, LabelName),	[readPageExecutable1,
								         updateAgentState(tiredness, continueRespondToError),
								         printMessage('Click Link Error 6 0 fixed\n')])
	:-	succeeded(toolsForWorkflow_browserClickLink(LabelName)), !
.
goalRequirements(continueRespondToError(clickLink, 0, LabelName),
	         [printMessage('Failed to click link second time\nDO A RESET\n')]).


%-------------------------
% Goal = RespondToMessage
%-------------------------
goalRequirements(respondToMessage(response(bugFixed)),	[startWork,
							printMessage('Concluded OK TO WORK\n'),
							getOnComputer(ID),
							removeBugs])
	:-	id(ID).

goalRequirements(respondToMessage(evil(true)),	[addPredicate(evil(true))]).

goalRequirements(respondToMessage(bug(1)),	[addPredicate(bug(1))]).

goalRequirements(respondToMessage(response(humanError)),	[startWork,
								 printMessage('IT couldn\'t fix it. Going to take a 5 min break\n'),
								 goToSleep(300),
								 getOnComputer(ID)])
	:-	id(ID).

goalRequirements(respondToMessage(error(spreadsheetValue, [Spreadsheet, Row, Col])),	
	         [printMessage('Error is not a computer error\n'),
									getOnComputer(ID),
									changeValue(Spreadsheet, Row, Col, Value),
									callPerson(IT, fixed(Spreadsheet, Row, Col)),
									removeErrorLog(1, [Spreadsheet, Row, Col]),
									startWork])
	:-	id(ID), myIT(IT),
		insertedValues(Spreadsheet, Row, Col, Value).

goalRequirements(respondToMessage(taskFillSpreadsheet(Spreadsheet, Size, Boolean)),
	[addPredicate(taskFillSpreadsheet(Spreadsheet, Size, Boolean))]).

goalRequirements(respondToMessage(Predicate), [addJobToStack, addPredicate(Predicate)]).


%-------------
% Effects of actions, in terms of updated beliefs
%-------------

% Get less tired on doNothing, though not below 0 (probably should set specific leisure activities)
updateBeliefs(doNothing,_) :- 
	check(agentState(tiredness,T)), T > 0, New is T - 0.5,
	execute(updateAgentState(tiredness, New)), !.

updateBeliefs(computer_applicationOpen(App),1) :- % Successful opening an app
	myRetract(appOpen(_)), myAssert(appOpen(App)),
	execute(updateAgentState(tiredness, App)), 
	execute(updateAgentState(unexpectedness, 0.05)), % As soon as it works once, we believe we're fine
	!.

updateBeliefs(computer_applicationSwitch(App),1) :- % Successful switch of focus
	myRetract(appHasFocus(_)), myAssert(appHasFocus(App)),
	execute(updateAgentState(tiredness, App)), 
	execute(updateAgentState(unexpectedness, 0.05)), 
	!.

updateBeliefs(computer_applicationSwitch(_),0) :-   % Failed
	execute(factorAgentState(unexpectedness, 1, 0.5)), % 'expectedness' halves each time, this is 1 - expectedness
	!.

updateBeliefs(computer_applicationOpen(_),0) :-   % Failed
	execute(factorAgentState(unexpectedness, 1, 0.5)), 
	!.


updateBeliefs(_,_).

							

%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%-----------------------------LIST OF Executables-------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

%executable(print(_)).
%execute(print(Message)) :- print(Message).

executable(startWork).
execute(startWork) :- myRetractall(okToWork(false)), myAssert(okToWork(true)).

executable(stopWork).
execute(stopWork) :- myRetractall(okToWork(true)), myAssert(okToWork(false)).

exucutable(removeBugs).
execute(removeBugs) :-	myRetractall(bug(_)).

executable(incrementFinishedTask(_, _, _)).
execute(incrementFinishedTask(Spreadsheet, Row, Col))
	:-	format('incrementing finished task\n', []),
	        check(taskFillCell(Spreadsheet, Row, Col)),
	        myRetract(taskFillCell(Spreadsheet, Row, Col)), 
	        check(finishedTasks(Temp1)),  % myRetract won't bind the value
		myRetract(finishedTasks(Temp1)),
		myRetractall(finishedTasks(_)),
		Temp2 is Temp1 + 1,
		myAssert(finishedTasks(Temp2)),
		myAssert(finishedTasks(Row)).

aexecutable(setUnknownValue(Spreadsheet, Row, Col)).
execute(setUnknownValue(Spreadsheet, Row, Col)) :- myAssert(cellVal(Spreadsheet, Row, Col, -1)).

% Value that gets set is random with probability that depends on tiredness
executable(setCellValue(Spreadsheet, Row, Col)).
execute(setCellValue(Spreadsheet, Row, Col))
	:- agentState(tiredness,Tiredness),
	   Tiredness < 0.85, !,
	   setValueProbabilistically(Spreadsheet, Row, Col, 0.95).
execute(setCellValue(Spreadsheet, Row, Col))
	:- setValueProbabilistically(Spreadsheet, Row, Col, 0.5).

setValueProbabilistically(Spreadsheet, Row, Col, ProbGood)
    :-  Badvalue is Row * 10,
	pickValueProbabilistically(ProbGood, Value, Row, Badvalue),
	myAssert(cellVal(Spreadsheet, Row, Col, Value)).

pickValueProbabilistically(ProbGood, Value, Goodvalue, _) :- ranf(X), X < ProbGood, !, Value is Goodvalue.
pickValueProbabilistically(_, Value, _, Badvalue) :- Value is Badvalue.
		
%executable(openBrowserExecutable1).
%execute(openBrowserExecutable1) :- myAssert(switchedApp(true)), myRetract(appOpen(_)), browserApp(Browser), myAssert(appOpen(Browser)).

%executable(openBrowserExecutable3).
%execute(openBrowserExecutable3) :- myAssert(browserOpen(true)), myRetract(appOpen(_)), browserApp(Browser), myAssert(appOpen(Browser)).

executable(readPageExecutable1).
execute(readPageExecutable1) :- myAssert(readValue(true)).

%executable(openSpreadsheetExecutable1).
%execute(openSpreadsheetExecutable1) :- myAssert(switchedApp(true)), myRetract(appOpen(_)), spreadsheetApp(Spreadsheet), myAssert(appOpen(Spreadsheet)).

executable(openSpreadsheetExecutable3).
execute(openSpreadsheetExecutable3) :- myAssert(spreadsheetOpen(true)), myRetract(appOpen(_)), spreadsheetApp(Spreadsheet), myAssert(appOpen(Spreadsheet)).

executable(insertValueExecutable1(Spreadsheet, Row, Col, Value)).
execute(insertValueExecutable1(Spreadsheet, Row, Col, Value)) :- myAssert(insertedValue(true)), myAssert(insertedValues(Spreadsheet, Row, Col, Value)).

executable(retractTask(Task)).
execute(retractTask(Task)) :- myRetract(Task).

executable(removeOpenSpreadsheet).
execute(removeOpenSpreadsheet) :- myRetractall(spreadsheetOpen(true)).

executable(checkExecutable).
execute(checkExecutable) :- myAssert(valueCorrect(true)).

executable(insertErrorLog(Error, Value)).
execute(inserrtErrorLog(Error, Value)) :- myAssert(tempError(Error, Value)).

exexutable(removeErrorLog(Error, Value)).
execute(removeErrorLog(Error, Value)) :- myRetract(tempError(Error, Value)).





%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%--------------------------LIST OF Primitive Actions----------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

primitiveAction(computer_applicationSwitch(_)).

primitiveAction(computer_applicationOpen(_)).
repeatable(computer_applicationOpen(_)).

primitiveAction(toolsForWorkflow_browserGoToAddress(_)).

primitiveAction(toolsForWorkflow_browserClickLink(_)).

primitiveAction(toolsForWorkflow_spreadsheetLogin(void)).

primitiveAction(toolsForWorkflow_spreadsheetSwitchSheet(_)).

primitiveAction(toolsForWorkflow_spreadsheetIsValue(Value, Row, Col)).

primitiveAction(toolsForWorkflow_spreadsheetSetValue(Value, Row, Col)).


%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Subgoals---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

subGoal(doOrdinaryWork).
subGoal(doEvilWork).
subGoal(checkInsertedValue).
subGoal(taskFillCell(Spreadsheet, Row, Col)).
subGoal(delegateTask(Task)).
subGoal(lookUpAndInsert(Spreadsheet, Row, Col)).
subGoal(getValues(Spreadsheet, Row, Col)).
subGoal(openSpreadsheet).
subGoal(insertValues(Spreadsheet, Row, Col)).
subGoal(reportAgent).

subGoal(openBrowser).
subGoal(readPage(Spreadsheet, Row, Col)).
subGoal(respondToError(Error, Value)).
subGoal(changeValue(Spreadsheet, Row, Col, Value)).
subGoal(check((Spreadsheet, Row, Col, Value))).

subGoal(continueChangeValue).
subGoal(continueCheck1(Spreadsheet)).
subGoal(continueCheck2(Spreadsheet, Row, Value)).
subGoal(continueDelegateTask(Task, ID)).
subGoal(continueOpenBrowser1).
subGoal(continueOpenBrowser2).
subGoal(continueReadPage1(Row, URL)).
subGoal(continueReadPage2(Row)).
subGoal(continueReadPage3(LabelName)).
subGoal(continueOpenSpreadsheet1).
subGoal(continueOpenSpreadsheet2).
subGoal(continueInsertValue1(Spreadsheet)).
subGoal(continueInsertValue2(Spreadsheet, Row, Col, Val)).
subGoal(continueInsertValue3(Spreadsheet, Row, Col, Val)).
subGoal(continueRespondToError(Error, Value)).


%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%
%------------------------------LIST OF Dynamics---------------------------------%
%-------------------------------------------------------------------------------%
%-------------------------------------------------------------------------------%

:-dynamic(computer_applicationSwitch/3).
:-dynamic(toolsForWorkflow_browserGoToAddress/2).
:-dynamic(toolsForWorkflow_browserClickLink/2).
:-dynamic(toolsForWorkflow_spreadsheetLogin/1).
:-dynamic(toolsForWorkflow_spreadsheetSwitchSheet/2).
:-dynamic(toolsForWorkflow_spreadsheetIsValue/4).
:-dynamic(toolsForWorkflow_spreadsheetSetValue/4).

:-dynamic(agentWorker/1).
:-dynamic(taskFillCell/3).
:-dynamic(unexpectedness/1).
:-dynamic(overWorkedThresh/1).
:-dynamic(cellVal/4).
:-dynamic(finishedTask/1).
:-dynamic(appHasFocus/1).
:-dynamic(appOpen/1).
:-dynamic(spreadsheetLoggedIn/1).
:-dynamic(website/1).
:-dynamic(taskMap/2).
:-dynamic(myManager/1).
:-dynamic(readValue/1).			%not used in code
:-dynamic(insertedValue/1).		%not used in code
:-dynamic(insertedValues/4).
:-dynamic(browserApp/1).
:-dynamic(spreadsheetApp/1).
:-dynamic(finishedTasks/1).
